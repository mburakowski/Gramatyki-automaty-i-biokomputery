"""Full training & evaluation pipeline.

This script trains a binary decision tree on labeled word examples,
converts the tree into a DFA, and compares the learned DFA with a
reference (teacher) DFA.

You can switch the target language using --language.
"""

import argparse
import random
from typing import Tuple

from languages.registry import get_language, list_languages
from generator import (
    generate_labeled_words,
    label_words_with_fp,
    label_words_with_fp_verbose,
    random_word_generator,
)
from decision_tree import build_tree
from tree_to_dfa import tree_to_dfa


def run_experiment(words, labels, true_dfa, alphabet, max_len: int, title: str):
    """Train -> convert -> evaluate for a single dataset.

    Partner change integrated:
      - we allow running the same pipeline on *noisy labels* (false positives)
        to demonstrate robustness / failure modes of the induction approach.
    """
    print(f"\n{title}")

    # 1) Train decision tree
    print("Training decision tree...")
    tree = build_tree(words, labels, max_depth=12)
    print("Tree trained.")

    # 2) Convert decision tree to DFA
    print("Converting tree to DFA...")
    learned_dfa = tree_to_dfa(tree, max_len=max_len, alphabet=alphabet)
    print("Conversion completed.")

    # 3) Agreement vs provided labels (can be noisy)
    correct = sum(learned_dfa.accepts(w) == lbl for w, lbl in zip(words, labels))
    train_acc = correct / len(words) if words else 0.0
    print(f"Training accuracy (vs provided labels): {train_acc:.3f}")

    # 4) Approximate equivalence vs true teacher DFA
    test_words = random_word_generator(2000, min_len=1, max_len=max_len, alphabet=alphabet)
    eq = all(learned_dfa.accepts(w) == true_dfa.accepts(w) for w in test_words)
    print(f"Equivalent to true DFA (random test): {eq}")

    return learned_dfa, train_acc, eq


def compute_accuracy(true_dfa, learned_dfa, words) -> float:
    """Computes acceptance agreement on a word list."""
    correct = 0
    for w in words:
        if learned_dfa.accepts(w) == true_dfa.accepts(w):
            correct += 1
    return correct / len(words) if words else 0.0


def run(
    language: str = "even_a",
    n_train: int = 2000,
    max_len: int = 10,
    seed: int = 123,
    fp_rate: float = 0.0,
    fp_seed: int | None = None,
    fp_verbose: bool = False,
) -> Tuple[float, bool]:
    """Runs training & evaluation for a selected language.

    By default, runs a clean (noise-free) experiment.
    If fp_rate > 0, it also runs additional experiments where we inject
    *false positives* into training labels.
    """

    random.seed(seed)

    lang = get_language(language)
    if max_len is None:
        max_len = getattr(lang, "DEFAULT_MAX_LEN", 10)

    # 1) Generate training data (clean labels)
    words, labels, true_dfa = generate_labeled_words(language, n_train, min_len=1, max_len=max_len, seed=seed)
    print(f"Language: {language}")
    print(f"Generated {len(words)} training samples.")

    learned_dfa, _train_acc_noisy, eq = run_experiment(
        words=words,
        labels=labels,
        true_dfa=true_dfa,
        alphabet=lang.ALPHABET,
        max_len=max_len,
        title="Base (clean labels)",
    )

    # For compatibility with earlier outputs, we still report "Accuracy" as
    # agreement teacher vs learned on the training set.
    train_acc = compute_accuracy(true_dfa, learned_dfa, words)
    print(f"Accuracy: {train_acc:.3f}")
    print(f"Equivalent: {eq}")

    # 2) Optional: experiments with false positives
    if fp_rate and fp_rate > 0.0:
        if fp_seed is None:
            fp_seed = seed

        data_fp = label_words_with_fp(true_dfa, words, fp_rate=fp_rate, seed=fp_seed)
        words_fp, labels_fp = zip(*data_fp)
        run_experiment(
            words=list(words_fp),
            labels=list(labels_fp),
            true_dfa=true_dfa,
            alphabet=lang.ALPHABET,
            max_len=max_len,
            title=f"Training with false positives (fp_rate={fp_rate:.2f})",
        )

        if fp_verbose:
            data_verbose = label_words_with_fp_verbose(true_dfa, words, fp_rate=fp_rate, seed=fp_seed)
            words_v = [w for w, _, _ in data_verbose]
            train_labels_v = [noisy for _, _, noisy in data_verbose]
            true_labels_v = [true for _, true, _ in data_verbose]

            learned_fp, _acc, _eq = run_experiment(
                words=words_v,
                labels=train_labels_v,
                true_dfa=true_dfa,
                alphabet=lang.ALPHABET,
                max_len=max_len,
                title="Training with FP (verbose / measured)",
            )

            tp = tn = fp = fn = 0
            for w, true_lbl in zip(words_v, true_labels_v):
                pred = learned_fp.accepts(w)
                if pred and true_lbl:
                    tp += 1
                elif (not pred) and (not true_lbl):
                    tn += 1
                elif pred and (not true_lbl):
                    fp += 1
                else:
                    fn += 1

            # avoid division by zero
            fp_rate_meas = fp / (fp + tn) if (fp + tn) else 0.0
            fn_rate_meas = fn / (fn + tp) if (fn + tp) else 0.0

            print(f"TP={tp}, TN={tn}, FP={fp}, FN={fn}")
            print(f"FP rate (measured): {fp_rate_meas:.3f}")
            print(f"FN rate (measured): {fn_rate_meas:.3f}")

    return train_acc, eq


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--language", "-l", default="even_a", choices=list_languages(), help="Target language")
    parser.add_argument("--n_train", "-n", type=int, default=2000, help="Number of training samples")
    parser.add_argument("--max_len", "-m", type=int, default=None, help="Maximum word length")
    parser.add_argument("--seed", type=int, default=123, help="Random seed")
    parser.add_argument("--fp_rate", type=float, default=0.0, help="Inject false positives into training labels")
    parser.add_argument("--fp_seed", type=int, default=None, help="Seed for false-positive injection")
    parser.add_argument("--fp_verbose", action="store_true", help="Print FP/FN stats for noisy-label experiment")

    args = parser.parse_args()
    run(
        language=args.language,
        n_train=args.n_train,
        max_len=args.max_len,
        seed=args.seed,
        fp_rate=args.fp_rate,
        fp_seed=args.fp_seed,
        fp_verbose=args.fp_verbose,
    )


if __name__ == "__main__":
    main()
