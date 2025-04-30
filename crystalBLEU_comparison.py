import json
import csv
import re
import os
import glob
from tqdm import tqdm
from collections import Counter
from crystalbleu import corpus_bleu
import fractions

# Monkey patch to fix crystalBLEU issue with Fraction
_orig_fraction_new = fractions.Fraction.__new__
def _fixed_fraction_new(cls, *args, **kwargs):
    kwargs.pop('_normalize', None)
    return _orig_fraction_new(cls, *args, **kwargs)

fractions.Fraction.__new__ = staticmethod(_fixed_fraction_new) 


# Helping auto-detect the programming language based on file extension
EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "c_sharp",
    ".rb": "ruby",
    ".go": "go",
    ".rs": "rust"
}
# Checks file extension and returns a language
def detect_language(filename: str):
    for ext, lang in EXTENSION_LANGUAGE_MAP.items():
        if filename.endswith(ext):
            print(f"\nlang found: {lang}")
            return lang
    print ("No language found and will return none")
    return None

# Removes comments depending on language
def strip_comments(code: str, language: str):
    if language == "python":
        return re.sub(r'#.*', '', code)
    elif language in ["javascript", "typescript", "java", "cpp", "c", "c_sharp", "go", "rust"]:
        code = re.sub(r'//.*', '', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code
    return code


# balanced regex tokenizer: extracts words, punctuation, and symbols
# Makes the code easier to compare in n-gram form
def tokenize_code(code: str, language: str):
    # Simple tokenizer: split on non-alphanumeric characters
    return re.findall(r"\w+|[^\s\w]", code)

# Turns token list into a list of n-grams
def extract_ngrams(tokens, n=1):
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

# Collects top k most frequent n-grams from the whole dataset to ignore during BLEU scoring
def get_trivially_shared_ngrams(corpus_tokens, top_k=500, ngram_range=(1, 4)):
    all_ngrams = []
    for tokens in corpus_tokens:
        for n in range(ngram_range[0], ngram_range[1] + 1):
            all_ngrams.extend(extract_ngrams(tokens, n))
    frequencies = Counter(all_ngrams)
    return dict(frequencies.most_common(top_k))

def process_commit_data(input_folder: str, output_csv_path: str, top_k=500, ngram_range=(1, 4)):
        
    # Get all JSON files in the folder
    json_files = glob.glob(os.path.join(input_folder, "*.json"))
    if not json_files:
        print(f"No JSON files found in folder: {input_folder}")
        return

    all_tokens_for_ngram_analysis = []

    files_processed = 0
    # collect all tokens for n-gram analysis
    for file_path in json_files:
        if files_processed >= 5:
            break
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
                continue
        files_processed += 1

    # Process each file       
    for item in data:
        language = detect_language(item.get("file", ""))
        if not language:
            continue

        before = strip_comments(item.get("before", ""), language)
        after = strip_comments(item.get("after", ""), language)

        try:
            tokens_before = tokenize_code(before, language)
            tokens_after = tokenize_code(after, language)
            all_tokens_for_ngram_analysis.append(tokens_before)
            all_tokens_for_ngram_analysis.append(tokens_after)

            for sugg in item.get("suggestions", []):
                tokens_sugg = tokenize_code(strip_comments(sugg.get("text", ""), language), language)
                all_tokens_for_ngram_analysis.append(tokens_sugg)
        except Exception as e:
            print(f"Skipping token collection due to error: {e}")
            continue

    # Build shared n-grams to ignore
    trivially_shared = get_trivially_shared_ngrams(all_tokens_for_ngram_analysis, top_k, ngram_range)

    results = []

    files_processed = 0
    # Clean and tokenize before, after, and suggestions code for all commits
    for file_path in json_files:
        if files_processed >= 5:
            break
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                commit = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
                continue
        files_processed += 1
        
    sha = commit.get("sha", "unknown")
    files_changed = commit.get("code", [])
    conversations = commit.get("chatgpt_sharing", {}).get("conversations", [])

    for file_change in files_changed:
        filename = file_change.get("filename", "")
        language = detect_language(filename)
        if not language:
            continue

        before = strip_comments(file_change.get("before", ""), language)
        after = strip_comments(file_change.get("after", ""), language)

        try:
            tokens_before = tokenize_code(before, language)
            tokens_after = tokenize_code(after, language)

            all_tokens_for_ngram_analysis.append(tokens_before)
            all_tokens_for_ngram_analysis.append(tokens_after)

            # Collect all model-generated code blocks
            best_bleu = 0.0
            best_prompt_id = None

            for prompt_id, convo in enumerate(conversations):
                code_blocks = convo.get("code", [])
                for code_obj in code_blocks:
                    code_content = code_obj.get("content", "")
                    try:
                        tokens_code = tokenize_code(strip_comments(code_content, language), language)
                        bleu = corpus_bleu([[tokens_after]], [tokens_code], ignoring=trivially_shared)
                        if bleu > best_bleu:
                            best_bleu = bleu
                            best_prompt_id = prompt_id
                    except Exception as e:
                        print(f"Error comparing code snippet in {filename}: {e}")
                        continue

            results.append({
                "sha": sha,
                "file": filename,
                "language": language,
                "best_bleu_after_vs_chatgpt": round(best_bleu, 4),
                "best_prompt_id": best_prompt_id
            })

        except Exception as e:
            print(f"Error processing file {filename} in {file_path}: {e}")
            continue


    if not results:
        print("⚠️  No valid results found. Check your input data or logic.")
        return
    
    # Write final results to a CSV file
    with open(output_csv_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ CrystalBLEU evaluation complete. Results saved to {output_csv_path}")

if __name__ == "__main__":
    process_commit_data("structured_Refactoring_Commits", "evaluation_results.csv")
