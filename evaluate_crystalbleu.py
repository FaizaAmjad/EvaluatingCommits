from utils.tokenization import tokenize_code
from crystalbleu import corpus_bleu, SmoothingFunction
import fractions

# Monkey patch to fix crystalBLEU issue with Fraction
_orig_fraction_new = fractions.Fraction.__new__
def _fixed_fraction_new(cls, *args, **kwargs):
    kwargs.pop('_normalize', None)
    return _orig_fraction_new(cls, *args, **kwargs)

fractions.Fraction.__new__ = staticmethod(_fixed_fraction_new) 


def evaluate_crystalbleu(tokens_after, tokens_code, trivially_shared):
    smoothing = SmoothingFunction(epsilon=0.0001).method1
    return corpus_bleu(
        [[tokens_after]],
        [tokens_code],
        smoothing_function=smoothing,
        ignoring=trivially_shared
    )

def find_prompt_with_highest_crystalbleu_score(after_code, conversations, trivially_shared):
    tokens_after = tokenize_code(after_code)
    best_score = 0.0
    best_prompt_id = None
    best_code = ""

    for convo in conversations:
        prompt_id = convo.get("prompt_id")
        for code_obj in convo.get("list_of_code", []):
            gpt_code = code_obj.get("Content", "")
            tokens_code = tokenize_code(gpt_code)

            score = evaluate_crystalbleu(tokens_after, tokens_code, trivially_shared)
            if score > best_score:
                best_score = score
                best_prompt_id = prompt_id
                best_code = gpt_code
    return best_score, best_prompt_id, best_code
