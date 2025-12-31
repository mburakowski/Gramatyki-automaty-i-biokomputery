import random
from typing import Iterable, List, Tuple

from dfa import DFA
from languages.registry import get_language


def random_word_generator(n, min_len=1, max_len=10, alphabet=('a', 'b')):
    """
    Generates n random words where word length is between min_len and max_len.
    :param n: number of words to generate
    :param min_len: min word length
    :param max_len: max word length
    :param alphabet: alphabet of symbols
    :return: list of generated words (string)
    """
    words = []
    for _ in range(n):
        L = random.randint(min_len, max_len)
        word = "".join(random.choice(alphabet) for _ in range(L))
        words.append(word)
    return words


def even_a_dfa():
    """Creates a reference DFA that accepts words with even number of 'a'."""
    return get_language("even_a").teacher_dfa()


def label_words(dfa: DFA, words: Iterable[str]) -> List[Tuple[str, bool]]:
    """
    Labels words using any DFA.
    Returns list of (word, label) pairs.
    """
    return [(w, dfa.accepts(w)) for w in words]


def label_words_with_fp(dfa: DFA, words: Iterable[str], fp_rate: float = 0.1, seed=None) -> List[Tuple[str, bool]]:
    """Labels words using a teacher DFA, but injects *false positives*.

    This is useful to test robustness of the learning pipeline against
    noisy labels. We only flip some negative examples to positive, i.e.:
      - label=True may include false positives
      - label=False is always correct

    :param dfa: teacher DFA
    :param words: iterable of words
    :param fp_rate: probability of flipping a negative example to True
    :param seed: optional RNG seed for reproducibility
    :return: list of (word, noisy_label)
    """
    if seed is not None:
        random.seed(seed)

    labeled: List[Tuple[str, bool]] = []
    for w in words:
        true_label = dfa.accepts(w)
        if (not true_label) and random.random() < fp_rate:
            labeled.append((w, True))
        else:
            labeled.append((w, true_label))

    return labeled


def label_words_with_fp_verbose(dfa: DFA, words: Iterable[str], fp_rate: float = 0.1, seed=None):
    """Verbose false-positive labeling.

    Returns triples (word, true_label, noisy_label), which makes it possible
    to measure false-positive / false-negative rates of the learned DFA.

    :param dfa: teacher DFA
    :param words: iterable of words
    :param fp_rate: probability of flipping a negative example to True
    :param seed: optional RNG seed for reproducibility
    :return: list of (word, true_label, noisy_label)
    """
    if seed is not None:
        random.seed(seed)

    data = []
    for w in words:
        true_label = dfa.accepts(w)
        noisy_label = true_label
        if (not true_label) and random.random() < fp_rate:
            noisy_label = True
        data.append((w, true_label, noisy_label))

    return data


def generate_labeled_words(language_name: str, n: int, min_len=1, max_len=10, seed=None):
    """Convenience helper used by training and tests.

    Generates n random words and labels them using the language's teacher DFA.
    """
    if seed is not None:
        random.seed(seed)

    lang = get_language(language_name)
    words = random_word_generator(n, min_len=min_len, max_len=max_len, alphabet=lang.ALPHABET)
    teacher = lang.teacher_dfa()
    labels = [teacher.accepts(w) for w in words]
    return words, labels, teacher
