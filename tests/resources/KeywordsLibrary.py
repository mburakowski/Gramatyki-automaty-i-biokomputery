"""Robot Framework keyword library for the project.

Provides:
- training of a decision tree for a selected language,
- conversion of the tree to a learned DFA,
- comparisons between teacher DFA and learned DFA.

Keywords are exposed as function names by Robot.
"""

import os
import sys
import random
from itertools import product
from typing import Dict, List, Tuple

# ensure project root is on PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from languages.registry import list_languages, get_language
from generator import random_word_generator
from decision_tree import build_tree
from tree_to_dfa import tree_to_dfa


_TEACHERS: Dict[str, object] = {}
_MODELS: Dict[str, object] = {}


def _get_teacher(language_name: str):
    if language_name not in _TEACHERS:
        lang = get_language(language_name)
        _TEACHERS[language_name] = lang.teacher_dfa()
    return _TEACHERS[language_name]


def _ensure_trained(language_name: str, n_train: int = 2000, max_len: int = 10, seed: int = 123):
    """Trains decision tree and converts it into DFA. Cached per language."""
    key = f"{language_name}|{n_train}|{max_len}|{seed}"
    if key in _MODELS:
        return _MODELS[key]

    random.seed(seed)
    lang = get_language(language_name)
    teacher = _get_teacher(language_name)

    words = random_word_generator(n_train, min_len=1, max_len=max_len, alphabet=lang.ALPHABET)
    labels = [teacher.accepts(w) for w in words]

    tree = build_tree(words, labels, max_depth=12)
    learned = tree_to_dfa(tree, max_len=max_len, alphabet=lang.ALPHABET)

    _MODELS[key] = (teacher, learned, words, labels)
    return _MODELS[key]


def _all_words(alphabet: Tuple[str, ...], max_len: int) -> List[str]:
    """Enumerates all words over alphabet with lengths 0..max_len."""
    out = [""]
    for L in range(1, max_len + 1):
        for tup in product(alphabet, repeat=L):
            out.append("".join(tup))
    return out



# Robot keywords
def list_available_languages():
    """Returns list of registered language names."""
    return list_languages()


def train_language(language_name: str, n_train: int = 2000, max_len: int = 10, seed: int = 123):
    """Trains and caches the learned DFA for a language.

    Returns (accuracy, equivalent_on_random_test).
    """
    teacher, learned, words, _labels = _ensure_trained(language_name, n_train=n_train, max_len=max_len, seed=seed)

    # accuracy on training set = agreement teacher vs learned
    correct = 0
    for w in words:
        if teacher.accepts(w) == learned.accepts(w):
            correct += 1
    acc = correct / len(words) if words else 0.0

    # approximate equivalence on random test
    lang = get_language(language_name)
    test_words = random_word_generator(1000, min_len=1, max_len=max_len, alphabet=lang.ALPHABET)
    eq = all(teacher.accepts(w) == learned.accepts(w) for w in test_words)

    return acc, eq


def teacher_accepts(language_name: str, word: str):
    """Returns True if the teacher DFA accepts the word."""
    teacher = _get_teacher(language_name)
    return teacher.accepts(word)


def learned_accepts(language_name: str, word: str, n_train: int = 2000, max_len: int = 10, seed: int = 123):
    """Returns True if the learned DFA accepts the word."""
    teacher, learned, _words, _labels = _ensure_trained(language_name, n_train=n_train, max_len=max_len, seed=seed)
    return learned.accepts(word)


def compare_dfas_exhaustive(language_name: str, max_len: int = 8, n_train: int = 2000, seed: int = 123):
    """Compares teacher vs learned DFA on ALL words up to max_len.

    Returns True if all results match.
    """
    lang = get_language(language_name)
    teacher, learned, _words, _labels = _ensure_trained(language_name, n_train=n_train, max_len=max(max_len, 1), seed=seed)

    for w in _all_words(lang.ALPHABET, max_len):
        if teacher.accepts(w) != learned.accepts(w):
            return False
    return True


def dfa_is_complete(language_name: str, n_train: int = 2000, max_len: int = 10, seed: int = 123):
    """Checks that the learned DFA has a defined transition for every (state, symbol)."""
    lang = get_language(language_name)
    _teacher, learned, _words, _labels = _ensure_trained(language_name, n_train=n_train, max_len=max_len, seed=seed)

    for s in learned.states:
        for sym in lang.ALPHABET:
            if learned.step(s, sym) is None:
                return False
    return True
