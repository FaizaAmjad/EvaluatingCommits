from tree_sitter_languages import get_parser
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

default_stopwords = {
    "(", ")", "{", "}", "[", "]", ":", ",", ".", ";",
    "=", "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=",
    "return", "if", "else", "for", "while", "def", "function", "var", "let", "const"
}

def tokenize_with_tree_sitter(code: str, language: str):
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

def filter_tokens(tokens, stopwords):
    return [tok for tok in tokens if tok not in stopwords]

def crystal_bleu(reference, hypothesis, stopwords, n_gram=4):
    filtered_reference = [filter_tokens(ref, stopwords) for ref in reference]
    filtered_hypothesis = filter_tokens(hypothesis, stopwords)
    smoothie = SmoothingFunction().method4
    return sentence_bleu(filtered_reference, filtered_hypothesis, weights=[1/n_gram]*n_gram, smoothing_function=smoothie)

# Sample codes (Python, JavaScript, etc.)
committed_code = "function add(a, b) { return a + b; }"
chatgpt_code = "function add(x, y) { return x + y; }"

# Tokenize using Tree-sitter (auto handles language syntax)
ref_tokens = tokenize_with_tree_sitter(committed_code, "Python")
hyp_tokens = tokenize_with_tree_sitter(chatgpt_code, "Python")

# Score
score = crystal_bleu([ref_tokens], hyp_tokens, stopwords=default_stopwords)
print("CrystalBLEU Score:", score)
