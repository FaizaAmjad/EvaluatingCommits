import re


def strip_comments(code: str) -> str:
    # Remove single-line comments (#, //) and multi-line comments (/* ... */)
    code = re.sub(r'#.*', '', code)                     # Python-style
    code = re.sub(r'//.*', '', code)                    # C/C++/Java/JS-style
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)  # Multiline
    return code

# balanced regex tokenizer: extracts words, punctuation, and symbols
# Makes the code easier to compare in n-gram form
def tokenize_code(code: str):
    # Simple tokenizer: split on non-alphanumeric characters
    return re.findall(r"\w+|[^\s\w]", code)

# Turns token list into a list of n-grams
def extract_ngrams(tokens, n=1):
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
