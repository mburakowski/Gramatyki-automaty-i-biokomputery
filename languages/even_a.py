"""Language: even number of 'a'.

L = { w in {a,b}* : count_a(w) is even }
"""

from dfa import DFA

NAME = "even_a"
ALPHABET = ("a", "b")
DEFAULT_MAX_LEN = 10


def teacher_dfa():
    """Creates the reference DFA for even number of 'a'."""
    d = DFA(alphabet=ALPHABET)

    # q0 = even a-count (accepting)
    # q1 = odd a-count
    d.add_state(0, accepting=True)
    d.add_state(1, accepting=False)
    d.set_start(0)

    # flip on 'a'
    d.add_transition(0, "a", 1)
    d.add_transition(1, "a", 0)

    # stay on 'b'
    d.add_transition(0, "b", 0)
    d.add_transition(1, "b", 1)

    return d


def describe():
    return "Words over {a,b} with even number of 'a'."
