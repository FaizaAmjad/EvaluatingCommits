import json
import csv
import re
import os
import glob
from collections import Counter
from crystalbleu import corpus_bleu, SmoothingFunction
import fractions
from evaluate_dev_gpt_score import score_dev_vs_gpt_changes
import time

### Global Variables ###
DEBUG_OUTPUT = True

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
        raise ZeroDivisionError  # Avoid division by zero

    match_count = sum(1 for line in suggestion_lines if line in after_lines)
    return match_count / len(suggestion_lines)

def evaluate_crystalbleu_scores(file_paths, trivially_shared, output_csv_path):
    
    results = []
    samples_folder = "samples"
    disallowed_exts = {'.sh', '.exe', '.bat', '.md', '.yaml'}

    # make directory for the samples, if folder exists raise error
    folder_creation_success = True
    try:
        os.makedirs(samples_folder, exist_ok=False)
    except:
        print("ERROR! Delete \"samples\" folder to create a new one.")
        folder_creation_success = False
        time.sleep(3)

    i = 0
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                commit = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
                continue

        sha = commit.get("sha", "unknown")
        link_to_github_commit = commit.get("url", "")
        files_changed = commit.get("code", [])
        conversations = commit.get("chatgpt_sharing", {}).get("conversations", [])

        for file_change in files_changed:
            if not isinstance(file_change, dict):
                print(f"Skipping malformed file_change in {file_path}: {file_change}")
                continue
            filename = file_change.get("filename", "")
            before = file_change.get("before", "")
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
                best_prompt_convo = None

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
                            try:
                                line_match_score = compute_line_exact_match(after, code_content)
                            except ZeroDivisionError:
                                print("compute_line_exact_match() failed")
                                line_match_score = 0.0


                        if crystalbleu_score > best_crystalbleu:
                            best_crystalbleu = crystalbleu_score
                            best_prompt_id = prompt_id
                            best_prompt_convo = convo

                        if line_match_score > best_line_match:
                            best_line_match = line_match_score
                            best_match_prompt_id = prompt_id
                            
                
                dev_changed_score = 0.0
                gpt_reused_score = 0.0

                # Calculate dev_changed and gpt_reused_score
                if best_prompt_convo:
                    dev_changed_score, gpt_reused_score =  score_dev_vs_gpt_changes(before, after, best_prompt_convo)

                results.append({
                    "sha": sha,
                    "file": filename,
                    "best_crystalbleu_after_vs_chatgpt": round(best_crystalbleu, 4),
                    "best_prompt_id": best_prompt_id,
                    "line_exact_match": round(best_line_match, 4),
                    "line_match_prompt_id": best_match_prompt_id,
                    "dev_changed_score": round(dev_changed_score, 4),
                    "gpt_reused_score": round(gpt_reused_score, 4)
                })

                # add all code files to the "samples" folder
                if DEBUG_OUTPUT and folder_creation_success:
                    if any(filename.endswith(ext) for ext in disallowed_exts): #checks if filename ends with an extension that implies the file is not code, eg.  .md  .exe  .sh  etc.
                        continue  # Skip this file
                    else:
                        best_crystalbleu = round(best_crystalbleu, 4)
                        best_line_match = round(best_line_match, 4)
                        create_sample(filename, i, sha, best_line_match, link_to_github_commit, best_crystalbleu, developer_written_lines="test", chatGPT_written_lines="test", exact_match_lines="test", chatGPT_code_with_match_greater_than_half=[])
                        i = i+1

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

def create_sample(filename, number, sha, rate_of_exact_match, link_to_github, crystalBLEU_result, developer_written_lines, chatGPT_written_lines, exact_match_lines, chatGPT_code_with_match_greater_than_half : list):

    samples_folder = "samples"
    # make directory (folder) with name being the enumerated number ie. 0, 1, 2, ...
    try:
        folder = os.path.join(samples_folder, f"{number}")
        os.makedirs(folder, exist_ok=False)
    except OSError:
        print(f"OSError for sha: {sha}, sample number: {number}")
        return
    
    # make directory (folder) with name "chatGPT_code_with_high_similarity"
    try:
        folder_2 = os.path.join(folder, "chatGPT_code_with_high_similarity")
        os.makedirs(folder_2, exist_ok=False)
    except OSError:
        print(f"OSError for sha: {sha}, sample number: {number}")
        return
        
    #set paths for all the files in the folder
    info_path = os.path.join(folder, "info.json")
    exact_match_path = os.path.join(folder, "exact_match")
    developer_written_lines_path = os.path.join(folder, "developer_written_lines")
    chatGPT_written_lines_path = os.path.join(folder, "chatGPT_written_lines")
    

    try:
        # Write metadata to info.json
        metadata = {
            "number": number,
            "sha": sha,
            "crystalBLEU_result": crystalBLEU_result,
            "rate_of_exact_match": rate_of_exact_match,
            "link_to_github": link_to_github,
            "filename": filename
        }
        with open(info_path, 'w', encoding='utf-8') as ip:
            json.dump(metadata, ip, indent=6)

        with open(exact_match_path, 'w', encoding='utf-8') as emp:
            json.dump("placeholder", emp, indent=6)

        with open(developer_written_lines_path, 'w', encoding='utf-8') as dwlp:
            json.dump("placeholder", dwlp, indent=6)

        with open(chatGPT_written_lines_path, 'w', encoding='utf-8') as cwlp:
            json.dump("placeholder", cwlp, indent=6)

        i = 0
        for code in chatGPT_code_with_match_greater_than_half:
            #set path for the file
            extra_code_path = os.path.join(folder_2, f"{i}")
            with open(extra_code_path, 'w', encoding='utf-8') as ecp:
                json.dump("placeholder", ecp, indent=6)
            i=i+1
        
        print(f"✅ Sampled and saved: {filename}")
    except Exception as write_err:
        try:
            #clean up after os.makedirs() if needed
            os.rmdir(os.path.join(folder_2))
            os.rmdir(os.path.join(folder))
        except FileNotFoundError:
            pass 
        except OSError:
            pass
        except Exception as write_err_2:
            print(f"⚠️ Failed to cleanup after attempting to sample {filename}: {write_err} \n AND\n {write_err_2}")


 
def process_commit_data(input_folder: str, output_csv_path: str, top_k, ngram_range, file_limit):
    # Get all JSON files in the folder
    json_files = glob.glob(os.path.join(input_folder, "*.json"))[:file_limit]
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
    process_commit_data("Structured_Refactoring_Commits", "evaluation_results.csv", top_k=500, ngram_range=(1, 4), file_limit=5)
