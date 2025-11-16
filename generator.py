"""
Word generator and labeling utilities.
"""

import random
from dfa import DFA


def random_word_generator(n, min_len=1, max_len=10, alphabet=('a', 'b')):
    """
    Generates n random words where word length is between 1 and 10
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
    """
    Creates a reference DFA that accepts words with even number of 'a'.
    """
    d = DFA()
    d.add_state(0, accepting=True)
    d.add_state(1, accepting=False)
    d.set_start(0)

    d.add_transition(0, 'a', 1)
    d.add_transition(1, 'a', 0)
    d.add_transition(0, 'b', 0)
    d.add_transition(1, 'b', 1)

    return d


def label_words(dfa, words):
    """
    Labels words using any DFA.
    Returns list of (word, label) pairs.
    """
    return [(w, dfa.accepts(w)) for w in words]

