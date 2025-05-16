from collections import Counter
import json
from .tokenization import extract_ngrams

# Function to extract and return the most common n-grams from the corpus.
# The n-grams are generated from the tokens, and their frequencies are counted.
def get_trivially_shared_ngrams(corpus_tokens, top_k, ngram_range=(1, 4)):
    all_ngrams = [] # Initialize an empty list to hold all the n-grams found in the corpus.
    
    # Loop through each set of tokens in the corpus
    for tokens in corpus_tokens:
        # Loop over the ngram range (from 1 to n) to generate n-grams
        for n in range(ngram_range[0], ngram_range[1] + 1):
            all_ngrams.extend(extract_ngrams(tokens, n))
    # Count the frequency of each n-gram using the Counter class.
    frequencies = Counter(all_ngrams)
    # Return the most common top_k n-grams as a dictionary.
    return dict(frequencies.most_common(top_k))

# Function to collect tokens for n-gram analysis from multiple JSON files.
# It processes code before and after changes, as well as ChatGPT conversation code objects.
def collect_tokens_for_ngram_analysis(file_paths, tokenize_fn):
    all_tokens = [] # List to store all tokens collected from the files.
    
    # Iterate over the list of file paths to process each file.
    for file_path in file_paths:    
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Process the 'code' key from the JSON, if available, extracting tokens for both 'before' and 'after' fields.        
        for file in data.get("code", []):
            all_tokens.append(tokenize_fn(file.get("before", "")))
            all_tokens.append(tokenize_fn(file.get("after", "")))
    # Process the 'chatgpt_sharing' key and extract tokens from the conversations and code objects.
        
        for convo in data.get("chatgpt_sharing", {}).get("conversations", []):
            for code_obj in convo.get("list_of_code", []):
                all_tokens.append(tokenize_fn(code_obj.get("Content", "")))
    
    # Return the collected tokens for further analysis.   
    return all_tokens
