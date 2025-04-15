import json
import csv
import re
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

# regex tokenizer: extracts words, punctuation, and symbols
# Makes the code easier to compare in n-gram form
def tokenize_code(code: str, language: str):
    # Simple tokenizer: split on non-alphanumeric characters
    return re.findall(r"\b\w+\b", code)

# Turns token list into a list of n-grams
def extract_ngrams(tokens, n=1):
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]

# Collects top k most frequent n-grams from the whole dataset to ignore during BLEU scoring
def get_trivially_shared_ngrams(corpus_tokens, top_k=500, n=1):
    all_ngrams = []
    for tokens in corpus_tokens:
        all_ngrams.extend(extract_ngrams(tokens, n))
    frequencies = Counter(all_ngrams)
    return dict(frequencies.most_common(top_k))

def process_commit_data(input_path: str, output_csv_path: str, top_k=500, n=1):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_tokens_for_ngram_analysis = []

    # collect all tokens for n-gram analysis
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
    trivially_shared = get_trivially_shared_ngrams(all_tokens_for_ngram_analysis, top_k, n)

    results = []

    # Clean and tokenize before, after, and suggestions code for all commits
    for item in tqdm(data, desc="Processing commits"):
        commit_id = item.get("commit_id")
        filename = item.get("file")
        language = detect_language(filename)
        if not language:
            continue

        before = strip_comments(item.get("before", ""), language)
        after = strip_comments(item.get("after", ""), language)

        try:
            tokens_before = tokenize_code(before, language)
            tokens_after = tokenize_code(after, language)
        except Exception as e:
            print(f"Skipping commit due to tokenization error: {e}")
            continue

        for suggestion in item.get("suggestions", []):
            suggestion_id = suggestion.get("id", "unknown")
            try:
                tokens_sugg = tokenize_code(strip_comments(suggestion.get("text", ""), language), language)
           
                bleu_after_vs_sugg = corpus_bleu([[tokens_after]], [tokens_sugg], ignoring=trivially_shared)
                bleu_after_vs_before = corpus_bleu([[tokens_after]], [tokens_before], ignoring=trivially_shared)
                bleu_sugg_vs_before = corpus_bleu([[tokens_sugg]], [tokens_before], ignoring=trivially_shared)

                results.append({
                    "commit_id": commit_id,
                    "file": filename,
                    "suggestion_id": suggestion_id,
                    "bleu_after_vs_sugg": round(bleu_after_vs_sugg, 4),
                    "bleu_after_vs_before": round(bleu_after_vs_before, 4),
                    "bleu_sugg_vs_before": round(bleu_sugg_vs_before, 4),
                    "language": language
                })
            except Exception as e:
                print(f"Skipping suggestion due to error: {e}")
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
    process_commit_data("test_commits.json", "results.csv")
