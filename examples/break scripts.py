# Takes every good script and produced mangled copies.
# Mangling methods:
# - Remove type annotations
# - Remove comments / docstrings
# - Remove tests
# - Add bugs
# -- Obvious errors
# -- Subtle errors
# - Rewriting to have correct output but just be worse. Slow, inefficient, poorly named, etc.

# Specific errors will be encoded in comments at top of file to be filtered out when evaluating.