def compute_exact_line_matches(after_code, gpt_code):
    after_lines = set(line.strip() for line in after_code.splitlines() if line.strip())
    gpt_lines = set(line.strip() for line in gpt_code.splitlines() if line.strip())

    if not after_lines:
        return 0.0
    matches = after_lines & gpt_lines
    return len(matches) / len(after_lines)

def evaluate_lines(after_code, gpt_code):
    exact_match_score = compute_exact_line_matches(after_code, gpt_code)
    return exact_match_score
