import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import json
from dataclasses import dataclass
from typing import List

@dataclass
class Turn:
    timestamp: float
    user: str
    prompt: str
    completion: str

class CopyButton(tk.Button):
    def __init__(self, master, target_widget, **kwargs):
        super().__init__(master, text="⧉", command=self.copy_to_clipboard, **kwargs)
        self.target_widget = target_widget
        self.config(width=2, height=1, relief=tk.FLAT, padx=0, pady=0, activebackground="white", bd=0, font=("Arial", 8))
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def copy_to_clipboard(self):
        self.clipboard_clear()
        if isinstance(self.target_widget, TurnWidget):
            turn_data = {
                "timestamp": self.target_widget.timestamp.timestamp(),
                "user": self.target_widget.user,
                "prompt": self.target_widget.prompt,
                "completion": self.target_widget.completion
            }
            self.clipboard_append(json.dumps(turn_data, indent=2))
        elif isinstance(self.target_widget, TurnLog):
            self.target_widget.copy_to_clipboard()
        else:
            self.clipboard_append(self.target_widget.get("1.0", tk.END).strip())

    def on_enter(self, event):
        self.config(fg="blue")

    def on_leave(self, event):
        self.config(fg="black")


class MessageTextBox(ttk.Frame):
    def __init__(self, master, text, **kwargs):
        super().__init__(master, **kwargs, padding=3)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.text_widget = tk.Text(self, wrap=tk.WORD, height=4, width=50, state='disabled', relief=tk.SOLID, bg='#FFFACD')
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        self.set_text(text)
        self.copy_button = CopyButton(self, self.text_widget, bg="#FFFACD")
        self.copy_button.config(font=("Arial", 7))
        
        self.copy_button.place(relx=1.0, rely=0, x=-2, y=2, anchor=tk.NE)

        # Bind the <Configure> event to adjust the height when the widget is resized
        self.text_widget.bind("<Configure>", self.adjust_height)

    def set_text(self, text):
        self.text_widget.config(state='normal')
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, text)
        self.text_widget.config(state='disabled')
        self.adjust_height()

    def adjust_height(self, event=None):
        if event is None or event.widget == self.text_widget:
            self.text_widget.config(height=self.text_widget.count("1.0", "end", "displaylines")[0])


class TurnWidget(ttk.Frame):
    def __init__(self, master, timestamp, user, prompt, completion, **kwargs):
        super().__init__(master, **kwargs)

        self.timestamp = datetime.fromtimestamp(timestamp)
        self.user = user
        self.prompt = prompt
        self.completion = completion

        self.create_widgets()

    def create_widgets(self):
        self.top_frame = ttk.Frame(self)
        self.top_frame.grid(row=0, column=0, sticky="ew")

        self.user_label = ttk.Label(self.top_frame, text=self.user)
        self.user_label.pack(side=tk.LEFT)

        self.copy_turn_button = CopyButton(self.top_frame, self)
        self.copy_turn_button.pack(side=tk.RIGHT)

        self.prompt_textbox = MessageTextBox(self, self.prompt)
        self.prompt_textbox.grid(row=1, column=0, sticky="ew")

        self.completion_textbox = MessageTextBox(self, self.completion)
        self.completion_textbox.grid(row=2, column=0, sticky="ew")

        self.bottom_frame = ttk.Frame(self)
        self.bottom_frame.grid(row=3, column=0, sticky="ew")

        self.show_prompt_var = tk.BooleanVar(value=True)
        style = ttk.Style()
        style.configure("CustomCheckbutton.TCheckbutton", font=("Arial", 8))

        self.show_prompt_check = ttk.Checkbutton(self.bottom_frame, text="Show Prompt", variable=self.show_prompt_var, command=self.toggle_prompt, style="CustomCheckbutton.TCheckbutton")
        self.show_prompt_check.pack(side=tk.LEFT)

        self.timestamp_label = ttk.Label(self.bottom_frame, text=self.timestamp.strftime("%Y-%m-%d %H:%M:%S"), font=("Arial", 8), anchor=tk.E)
        self.timestamp_label.pack(side=tk.RIGHT)

        # Configure the weights for the TurnWidget
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.top_frame.columnconfigure(0, weight=1)

    def toggle_prompt(self):
        if self.show_prompt_var.get():
            self.prompt_textbox.grid(row=1, column=0, sticky="ew")
        else:
            self.prompt_textbox.grid_remove()

class TurnLog(ttk.Frame):
    def __init__(self, master, turns: List[Turn], **kwargs):
        super().__init__(master, **kwargs)
        self.turns = turns
        self.create_widgets()
        
        

    def create_widgets(self):
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill=tk.X)

        self.toggle_prompts_var = tk.BooleanVar(value=True)
        self.toggle_prompts_check = ttk.Checkbutton(self.top_frame, text="Toggle Prompts", variable=self.toggle_prompts_var, command=self.toggle_all_prompts)
        self.toggle_prompts_check.pack(side=tk.LEFT)

        self.copy_turns_button = CopyButton(self.top_frame, self)
        self.copy_turns_button.config(font=("Arial", 10))  # Set the font size to the default size
        self.copy_turns_button.pack(side=tk.RIGHT)

        self.save_button = ttk.Button(self.top_frame, text="Save", command=self.save_turns)
        self.save_button.pack(side=tk.RIGHT)

        self.load_button = ttk.Button(self.top_frame, text="Load", command=self.load_turns)
        self.load_button.pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(self, bd=0, relief=tk.FLAT, highlightthickness=0)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind("<Enter>", self.set_canvas_focus)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.scrollable_frame.bind("<MouseWheel>", self.on_mouse_wheel)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        

        for turn in self.turns:
            turn_widget = TurnWidget(self.scrollable_frame, turn.timestamp, turn.user, turn.prompt, turn.completion)
            turn_widget.pack(fill=tk.X, padx=10, pady=10)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_canvas_configure(self, event):
        width = event.width
        self.canvas.itemconfig(self.canvas.find_all()[0], width=width)

    def set_canvas_focus(self, event):
        self.canvas.focus_set()

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(-int(event.delta / 120), "units")

    def toggle_all_prompts(self):
        for child in self.scrollable_frame.winfo_children():
            if isinstance(child, TurnWidget):
                child.show_prompt_var.set(self.toggle_prompts_var.get())
                child.toggle_prompt()

    def copy_to_clipboard(self):
        self.clipboard_clear()
        turns_data = [
            {
                "timestamp": turn.timestamp,
                "user": turn.user,
                "prompt": turn.prompt,
                "completion": turn.completion
            }
            for turn in self.turns
        ]
        self.clipboard_append(json.dumps(turns_data, indent=2))

    def save_turns(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return

        turns_data = [
            {
                "timestamp": turn.timestamp,
                "user": turn.user,
                "prompt": turn.prompt,
                "completion": turn.completion
            }
            for turn in self.turns
        ]

        with open(file_path, "w") as file:
            json.dump(turns_data, file, indent=2)

    def load_turns(self):
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return

        with open(file_path, "r") as file:
            turns_data = json.load(file)

        self.turns = [Turn(**turn_data) for turn_data in turns_data]
        self.update_turns()

    def update_turns(self):
        for child in self.scrollable_frame.winfo_children():
            child.destroy()

        for turn in self.turns:
            turn_widget = TurnWidget(self.scrollable_frame, turn.timestamp, turn.user, turn.prompt, turn.completion)
            turn_widget.pack(fill=tk.X, padx=10, pady=10)



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Turn Log")

    turns = [
        Turn(1633036800, "User1", "This is a sample prompt 1.", "This is a sample completion 1."),
        Turn(1633036900, "User2", "This is a sample prompt 2.", "This is a sample completion 2."),
        Turn(1633037000, "User3", "This is a sample prompt 3.", "This is a sample completion 3."),
    ]

    turn_log = TurnLog(root, turns)
    turn_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    root.bind("<MouseWheel>", turn_log.on_mouse_wheel)

    root.mainloop()