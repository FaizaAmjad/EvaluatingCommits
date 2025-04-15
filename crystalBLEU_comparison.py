import os
from pathlib import Path
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from tree_sitter_languages import get_parser

# Basic stopwords used in most languages
DEFAULT_STOPWORDS = {
    "(", ")", "{", "}", "[", "]", ":", ",", ".", ";",
    "=", "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
    "return", "if", "else", "for", "while", "def", "function", "var", "let", "const"
}

# File extension to Tree-sitter language map
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

def detect_language(file_path: str):
    ext = Path(file_path).suffix
    return EXTENSION_LANGUAGE_MAP.get(ext, None)

def tokenize_code(code: str, language: str):
    try:
        parser = get_parser(language)
        tree = parser.parse(bytes(code, "utf8"))
        root_node = tree.root_node
        tokens = []

        def extract_tokens(node):
            if node.child_count == 0:
                tok = code[node.start_byte:node.end_byte]
                if tok.strip():
                    tokens.append(tok)
            else:
                for child in node.children:
                    extract_tokens(child)

        extract_tokens(root_node)
        return tokens
    except Exception as e:
        print(f"Tokenization failed for language {language}: {e}")
        return []

def filter_tokens(tokens, stopwords):
    return [tok for tok in tokens if tok not in stopwords]

def crystal_bleu(reference, hypothesis, stopwords, n_gram=4):
    filtered_reference = [filter_tokens(ref, stopwords) for ref in reference]
    filtered_hypothesis = filter_tokens(hypothesis, stopwords)
    smoothie = SmoothingFunction().method4
    return sentence_bleu(filtered_reference, filtered_hypothesis,
                         weights=[1/n_gram]*n_gram,
                         smoothing_function=smoothie)

def load_code(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Failed to read {filepath}: {e}")
        return ""

def compare_directories(committed_dir, chatgpt_dir):
    scores = []
    files = os.listdir(committed_dir)

    for filename in files:
        committed_path = os.path.join(committed_dir, filename)
        chatgpt_path = os.path.join(chatgpt_dir, filename)

        if not os.path.exists(chatgpt_path):
            print(f"[!] No ChatGPT version found for {filename}")
            continue

        language = detect_language(committed_path)
        if not language:
            print(f"[!] Skipping unsupported file: {filename}")
            continue

        committed_code = load_code(committed_path)
        chatgpt_code = load_code(chatgpt_path)

        ref_tokens = tokenize_code(committed_code, language)
        hyp_tokens = tokenize_code(chatgpt_code, language)

        if not ref_tokens or not hyp_tokens:
            print(f"[!] Skipping {filename} due to tokenization failure.")
            continue

        score = crystal_bleu([ref_tokens], hyp_tokens, stopwords=DEFAULT_STOPWORDS)
        print(f"{filename}: CrystalBLEU = {score:.4f}")
        scores.append(score)

    if scores:
        avg = sum(scores) / len(scores)
        print(f"\n✅ Average CrystalBLEU across {len(scores)} files: {avg:.4f}")
    else:
        print("No valid file comparisons found.")

# CLI usage
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare committed vs ChatGPT-generated code using CrystalBLEU.")
    parser.add_argument("committed_dir", help="Directory of final committed code")
    parser.add_argument("chatgpt_dir", help="Directory of ChatGPT-suggested code")

    args = parser.parse_args()
    compare_directories(args.committed_dir, args.chatgpt_dir)
