"""Language: strings that do NOT contain substring 'bb'.

L = { w in {a,b}* : 'bb' is not a substring of w }
"""

from dfa import DFA

NAME = "no_bb"
ALPHABET = ("a", "b")
DEFAULT_MAX_LEN = 10


def teacher_dfa():
    """Creates the reference DFA for forbidding 'bb'."""
    d = DFA(alphabet=ALPHABET)

    # q0: last symbol is not 'b' (or empty)
    # q1: last symbol is 'b'
    # q2: already saw 'bb' (rejecting sink)
    d.add_state(0, accepting=True)
    d.add_state(1, accepting=True)
    d.add_state(2, accepting=False)
    d.set_start(0)

    d.add_transition(0, "a", 0)
    d.add_transition(0, "b", 1)

    d.add_transition(1, "a", 0)
    d.add_transition(1, "b", 2)

    d.add_transition(2, "a", 2)
    d.add_transition(2, "b", 2)

    return d


def describe():
    return "Words over {a,b} that do not contain the substring 'bb'."
