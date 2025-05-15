from collections import Counter
import json
from .tokenization import extract_ngrams

def get_trivially_shared_ngrams(corpus_tokens, top_k, ngram_range=(1, 4)):
    all_ngrams = []
    for tokens in corpus_tokens:
        for n in range(ngram_range[0], ngram_range[1] + 1):
            all_ngrams.extend(extract_ngrams(tokens, n))
    frequencies = Counter(all_ngrams)
    return dict(frequencies.most_common(top_k))

def collect_tokens_for_ngram_analysis(file_paths, tokenize_fn):
    all_tokens = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for file in data.get("code", []):
            all_tokens.append(tokenize_fn(file.get("before", "")))
            all_tokens.append(tokenize_fn(file.get("after", "")))
        for convo in data.get("chatgpt_sharing", {}).get("conversations", []):
            for code_obj in convo.get("list_of_code", []):
                all_tokens.append(tokenize_fn(code_obj.get("Content", "")))
    return all_tokens
