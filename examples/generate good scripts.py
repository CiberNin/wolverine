import os
import sys
import itertools
from typing import List, Tuple
import openai

def read_openai_key() -> str:
    with open("../openai_key.txt", "r") as key_file:
        return key_file.read().strip()

def scan_good_scripts_directory() -> List[Tuple[str, str]]:
    existing_concept_pairs = []
    good_scripts_path = "good_scripts"

    for script_file in os.listdir(good_scripts_path):
        with open(os.path.join(good_scripts_path, script_file), "r") as file:
            first_line = file.readline().strip()
            if first_line:
                first_line = first_line[1:]
                concepts = first_line.split(",")
                if len(concepts) == 2:
                    existing_concept_pairs.append((concepts[0].strip(), concepts[1].strip()))

    return existing_concept_pairs

def generate_new_concept_pairs(existing_pairs: List[Tuple[str, str]], n: int) -> List[Tuple[str, str]]:
    openai.api_key = read_openai_key()
    new_pairs = []

    while len(new_pairs) < n:
        prompt = "Generate a list of new unique Python concept pairs that are not in the following list:\n"
        for pair in existing_pairs + new_pairs:
            prompt += f"{pair[0]}, {pair[1]}\n"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=50,
                n=1,
                stop=None,
                temperature=0.7,
            )
        except openai.error.InvalidRequestError:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=50,
                n=1,
                stop=None,
                temperature=0.7,
            )

        generated_pairs = response.choices[0].text.strip().split("\n")
        for pair in generated_pairs:
            concepts = pair.split(",")
            if len(concepts) == 2:
                new_pair = (concepts[0].strip(), concepts[1].strip())
                if new_pair not in existing_pairs and new_pair[::-1] not in existing_pairs:
                    new_pairs.append(new_pair)

    return new_pairs[:n]

def generate_scripts(concept_pairs: List[Tuple[str, str]]) -> List[str]:
    openai.api_key = read_openai_key()
    scripts = []

    for pair in concept_pairs:
        prompt = f"Generate a high-quality Python script that uses both {pair[0]} and {pair[1]} concepts. "
        prompt += "The script should have type annotations, comments, and comprehensive tests. "
        prompt += "It should not have any permanent side effects, take more than a few seconds to run, "
        prompt += "require any specific configuration of the environment, or require any interaction."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=300,
                n=1,
                stop=None,
                temperature=0.7,
            )
        except openai.error.InvalidRequestError:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=300,
                n=1,
                stop=None,
                temperature=0.7,
            )

        script = f"{pair[0]}, {pair[1]}\n{response.choices[0].text.strip()}"
        scripts.append(script)

    return scripts

def save_scripts_to_directory(scripts: List[str]):
    good_scripts_path = "good_scripts"

    for i, script in enumerate(scripts):
        with open(os.path.join(good_scripts_path, f"script_{i+1}.py"), "w") as file:
            file.write(script)

def main():
    existing_pairs = scan_good_scripts_directory()
    new_pairs = generate_new_concept_pairs(existing_pairs, 5)
    scripts = generate_scripts(new_pairs)
    save_scripts_to_directory(scripts)

if __name__ == "__main__":
    main()