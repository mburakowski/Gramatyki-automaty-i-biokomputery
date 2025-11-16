import os
import sys

# ensure project root is on PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from generator import even_a_dfa

dfa = even_a_dfa()


def check_accepts(word):
    """
    Keyword for Robot Framework.
    Returns True if DFA accepts the given word.
    """
    return dfa.accepts(word)


def should_be_false(value):
    """
    Custom keyword: passes only if value is logically False.
    """
    if bool(value):
        raise AssertionError(f"Expected False, got {value!r}")
