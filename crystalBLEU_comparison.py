import json
import csv
import re
import os
import glob
from collections import Counter
from crystalbleu import corpus_bleu, SmoothingFunction
import fractions

# Monkey patch to fix crystalBLEU issue with Fraction
_orig_fraction_new = fractions.Fraction.__new__
def _fixed_fraction_new(cls, *args, **kwargs):
    kwargs.pop('_normalize', None)
    return _orig_fraction_new(cls, *args, **kwargs)

fractions.Fraction.__new__ = staticmethod(_fixed_fraction_new) 

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

# Collects top k most frequent n-grams from the whole dataset to ignore during BLEU scoring
def get_trivially_shared_ngrams(corpus_tokens, top_k, ngram_range=(1, 4)):
    all_ngrams = []
    for tokens in corpus_tokens:
        for n in range(ngram_range[0], ngram_range[1] + 1):
            all_ngrams.extend(extract_ngrams(tokens, n))
    frequencies = Counter(all_ngrams)
    return dict(frequencies.most_common(top_k))

def collect_tokens_for_ngram_analysis(file_paths):
    all_tokens = []
    
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                commit = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
                continue

        files_changed = commit.get("code", [])
        conversations = commit.get("chatgpt_sharing", {}).get("conversations", [])

        for file_change in files_changed:
            if not isinstance(file_change, dict):
                print(f"Skipping malformed file_change in {file_path}: {file_change}")
                continue
            filename = file_change.get("filename", "")
            before = file_change.get("before", "")
            after = file_change.get("after", "")

            # before = strip_comments(file_change.get("before", ""))
            # after = strip_comments(file_change.get("after", ""))

            try:
                tokens_before = tokenize_code(before)
                tokens_after = tokenize_code(after)
                all_tokens.append(tokens_before)
                all_tokens.append(tokens_after)

                for convo in conversations:
                    for code_obj in convo.get("code", []):
                        code_content = code_obj.get("Content", "")
                        tokens_code = tokenize_code(code_content)
                        all_tokens.append(tokens_code)

            except Exception as e:
                print(f"Skipping token collection in {filename} due to error: {e}")
                continue
    
    return all_tokens
# Check lines of exact match between final committed code (after) and ChatGPT code
def compute_line_exact_match(after_code: str, chatgpt_code: str) -> float:
    # Normalize and split into lines
    after_lines = set(line.strip() for line in after_code.strip().splitlines() if line.strip())
    suggestion_lines = [line.strip() for line in chatgpt_code.strip().splitlines() if line.strip()]

    if not suggestion_lines:
        return 0.0  # Avoid division by zero

    match_count = sum(1 for line in suggestion_lines if line in after_lines)
    return match_count / len(suggestion_lines)

def evaluate_crystalbleu_scores(file_paths, trivially_shared, output_csv_path):
    
    results = []
    
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                commit = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
                continue

        sha = commit.get("sha", "unknown")
        files_changed = commit.get("code", [])
        conversations = commit.get("chatgpt_sharing", {}).get("conversations", [])

        for file_change in files_changed:
            if not isinstance(file_change, dict):
                print(f"Skipping malformed file_change in {file_path}: {file_change}")
                continue
            filename = file_change.get("filename", "")
            # before = file_change.get("before", "")
            after = file_change.get("after", "")
            print (f"filename {filename}")
            #before = strip_comments(file_change.get("before", ""))
            #after = strip_comments(file_change.get("after", ""))

            try:
                # tokens_before = tokenize_code(before)
                tokens_after = tokenize_code(after)

                best_crystalbleu = 0.0
                best_prompt_id = None

                best_line_match = 0.0
                best_match_prompt_id = None

                # Compare after vs code snippets from conversations
                for convo in conversations:
                    prompt_id = convo.get("prompt_id")
                    # print (f"prompt_id {prompt_id}")
                    code_blocks = convo.get("list_of_code", [])
                    for code_obj in code_blocks:
                        code_content = code_obj.get("Content", "")
                        # print("CODE_CONTENT :", code_content)
                        tokens_code = tokenize_code(code_content)
                        # print("AFTER:", tokens_after)
                        # print("SUGGESTION CODE :", tokens_code)
                        # print("IGNORING:", len(trivially_shared))

                        sm_func = SmoothingFunction(epsilon=0.0001).method1

                        if tokens_after and tokens_code:
                            crystalbleu_score = corpus_bleu(
                                [[tokens_after]],  # wrap reference in a list
                                [tokens_code],     # wrap hypothesis in a list
                                smoothing_function=sm_func,
                                ignoring=trivially_shared
                            )
                            line_match_score = compute_line_exact_match(after, code_content)


                        if crystalbleu_score > best_crystalbleu:
                            best_crystalbleu = crystalbleu_score
                            best_prompt_id = prompt_id

                        if line_match_score > best_line_match:
                            best_line_match = line_match_score
                            best_match_prompt_id = prompt_id

                results.append({
                    "sha": sha,
                    "file": filename,
                    "best_crystalbleu_after_vs_chatgpt": round(best_crystalbleu, 4),
                    "best_prompt_id": best_prompt_id,
                    "line_exact_match": round(line_match_score, 4),
                    "line_match_prompt_id": best_match_prompt_id
                })

            except Exception as e:
                print(f"Skipping CrystalBLEU evaluation for {filename} due to error: {e}")
                continue

    # Write results to CSV
    if results:
        with open(output_csv_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ CrystalBLEU evaluation complete. Results saved to {output_csv_path}")
    else:
        print("⚠️ No valid results found. Check your input data or logic.")

 
def process_commit_data(input_folder: str, output_csv_path: str, top_k, ngram_range, file_limit):
    # Get all JSON files in the folder
    json_files = glob.glob(os.path.join(input_folder, "*.json"))
    if not json_files:
        print("No JSON files found in folder.")
        return

    # Collect all tokens for n-gram analysis
    all_tokens = collect_tokens_for_ngram_analysis(json_files)

    # Build trivially shared n-grams (ignore most frequent ones)
    trivially_shared = get_trivially_shared_ngrams(all_tokens, top_k, ngram_range)

    # Evaluate BLEU scores based on the trivially shared n-grams
    evaluate_crystalbleu_scores(json_files, trivially_shared, output_csv_path)

if __name__ == "__main__":
    process_commit_data("structured_Refactoring_Commits", "evaluation_results.csv", top_k=500, ngram_range=(1, 4), file_limit=5)
