from difflib import SequenceMatcher

def line_match(line, candidates, threshold=0.9):
    """Return True if the line is similar to any in candidates above the threshold."""
    for cand in candidates:
        if SequenceMatcher(None, line, cand).ratio() >= threshold:
            return True
    return False

def score_dev_vs_gpt_changes(before_code, after_code, gpt_code, threshold=0.9):
    before_lines = set(line.strip() for line in before_code.strip().splitlines() if line.strip())
    after_lines = set(line.strip() for line in after_code.strip().splitlines() if line.strip())
    gpt_lines = set(line.strip() for line in gpt_code.strip().splitlines() if line.strip())

    unchanged_lines = before_lines & after_lines
    added_lines = after_lines - unchanged_lines

    gpt_reused = set()
    dev_added = set()

    for line in added_lines:
        if line_match(line, gpt_lines, threshold):
            gpt_reused.add(line)
        else:
            dev_added.add(line)

    total_added = len(added_lines)
    dev_changed_score = len(dev_added) / total_added if total_added else 0
    gpt_reused_score = len(gpt_reused) / total_added if total_added else 0

    return dev_changed_score, gpt_reused_score