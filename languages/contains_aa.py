"""Language: strings containing substring 'aa'.

L = { w in {a,b}* : 'aa' is a substring of w }
"""

from dfa import DFA

NAME = "contains_aa"
ALPHABET = ("a", "b")
DEFAULT_MAX_LEN = 10


def teacher_dfa():
    """Creates the reference DFA for containing 'aa'."""
    d = DFA(alphabet=ALPHABET)

    # q0: no trailing 'a'
    # q1: last symbol was 'a'
    # q2: found 'aa' somewhere (accepting sink)
    d.add_state(0, accepting=False)
    d.add_state(1, accepting=False)
    d.add_state(2, accepting=True)
    d.set_start(0)

    d.add_transition(0, "a", 1)
    d.add_transition(0, "b", 0)

    d.add_transition(1, "a", 2)
    d.add_transition(1, "b", 0)

    d.add_transition(2, "a", 2)
    d.add_transition(2, "b", 2)

    return d


def describe():
    return "Words over {a,b} containing the substring 'aa'."
