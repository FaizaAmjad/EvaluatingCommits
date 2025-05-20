import os
import csv
import json
import glob

from utils.tokenization import tokenize_code
from utils.ngrams_analysis import collect_tokens_for_ngram_analysis, get_trivially_shared_ngrams
from evaluate_crystalbleu import find_prompt_with_highest_crystalbleu_score
from evaluate_line_match import evaluate_lines
from evaluate_dev_gpt_score import score_dev_vs_gpt_changes

def process_commits(input_folder: str, output_csv_path: str, top_k: int, ngram_range: tuple, file_limit: int = None):
    json_files = glob.glob(os.path.join(input_folder, "*.json"))
    if file_limit:
        json_files = json_files[:file_limit]

    if not json_files:
        print("No JSON files found.")
        return

    all_tokens = collect_tokens_for_ngram_analysis(json_files, tokenize_code)
    trivially_shared = get_trivially_shared_ngrams(all_tokens, top_k, ngram_range)

    results = []

    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                commit = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error parsing {file_path}: {e}")
                continue

        sha = commit.get("sha", "unknown")
        conversations = commit.get("chatgpt_sharing", {}).get("conversations", [])

        for file_change in commit.get("code", []):
            filename = file_change.get("filename")
            if not filename:
             print(f"⚠️ Skipping file with missing filename in {file_path}")
             continue
            before = file_change.get("before", "")
            after = file_change.get("after", "")

            try:
                best_crystalbleu_score, best_prompt_id, best_gpt_code = find_prompt_with_highest_crystalbleu_score(after, conversations, trivially_shared)
                line_match_score= evaluate_lines(after, best_gpt_code)
                dev_changed_score, gpt_reused_score =  score_dev_vs_gpt_changes(before, after, best_gpt_code)

                results.append({
                    "sha": sha,
                    "file": filename,
                    "prompt_id": best_prompt_id,
                    "crystalbleu_after_vs_chatgpt": round(best_crystalbleu_score, 4),
                    "line_match_after_vs_chatgpt": round(line_match_score, 4),
                    "dev_changed_lines_score": round(dev_changed_score, 4),
                    "gpt_reused_lines_score": round(gpt_reused_score, 4)
                })

            except Exception as e:
                print(f"Error processing {filename} in {file_path}: {e}")
                continue

    if results:
        with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Evaluation complete. Results saved to {output_csv_path}")
    else:
        print("⚠️ No valid results collected.")

if __name__ == "__main__":
    process_commits(
        input_folder="structured_Refactoring_Commits",
        output_csv_path="evaluation_results.csv",
        top_k=100,
        ngram_range=(1, 4),
        file_limit=None # Or use an integer like 5 for testing
    )
