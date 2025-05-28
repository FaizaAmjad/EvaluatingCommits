from nltk.metrics import edit_distance
from utils.tokenization import tokenize_code

def token_edit_ratio(a, b):
    """Compute Levenshtein ratio between tokenized code lines."""
    tokens_a = tokenize_code(a)
    tokens_b = tokenize_code(b)
    distance = edit_distance(tokens_a, tokens_b)
    max_len = max(len(tokens_a), len(tokens_b))
    return 1 - (distance / max_len) if max_len else 1

def score_dev_vs_gpt_changes(before_code, after_code, gpt_code, threshold=0.7):
    # before_lines = set(line.strip() for line in before_code.strip().splitlines() if line.strip())
    after_lines = set(line.strip() for line in after_code.strip().splitlines() if line.strip())
    gpt_lines = set(line.strip() for line in gpt_code.strip().splitlines() if line.strip())

    # unchanged_lines = before_lines & after_lines
    # added_lines = after_lines - unchanged_lines

    exact_matches = set()
    modified_matches = set()
    dev_original = set()

    for line in after_lines:
        best_ratio = max(token_edit_ratio(line, gpt_line) for gpt_line in gpt_lines)
        if best_ratio == 1.0:
            exact_matches.add(line)
        elif best_ratio >= threshold:
            modified_matches.add(line)
        else:
            dev_original.add(line)

    total_added = len(after_lines)
    exact_score = len(exact_matches) / total_added if total_added else 0
    modified_score = len(modified_matches) / total_added if total_added else 0
    dev_score = len(dev_original) / total_added if total_added else 0

    return exact_score, modified_score, dev_score