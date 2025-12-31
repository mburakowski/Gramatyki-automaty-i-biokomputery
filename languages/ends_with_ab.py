"""Language: strings ending with 'ab'.

L = { w in {a,b}* : w endswith 'ab' }
"""

from dfa import DFA

NAME = "ends_with_ab"
ALPHABET = ("a", "b")
DEFAULT_MAX_LEN = 10


def teacher_dfa():
    """Creates the reference DFA for the suffix pattern 'ab'."""
    d = DFA(alphabet=ALPHABET)

    # q0: no partial match
    # q1: last symbol was 'a'
    # q2: last two symbols were 'ab' (accepting)
    d.add_state(0, accepting=False)
    d.add_state(1, accepting=False)
    d.add_state(2, accepting=True)
    d.set_start(0)

    d.add_transition(0, "a", 1)
    d.add_transition(0, "b", 0)

    d.add_transition(1, "a", 1)
    d.add_transition(1, "b", 2)

    d.add_transition(2, "a", 1)
    d.add_transition(2, "b", 0)

    return d


def describe():
    return "Words over {a,b} ending with the suffix 'ab'."
