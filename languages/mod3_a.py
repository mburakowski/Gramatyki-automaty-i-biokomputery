"""Language: number of 'a' is congruent to 0 mod 3.

L = { w in {a,b}* : count_a(w) % 3 == 0 }
"""

from dfa import DFA

NAME = "mod3_a"
ALPHABET = ("a", "b")
DEFAULT_MAX_LEN = 10


def teacher_dfa():
    """Creates the reference DFA for count_a % 3 == 0."""
    d = DFA(alphabet=ALPHABET)

    # states represent a_count mod 3
    d.add_state(0, accepting=True)
    d.add_state(1, accepting=False)
    d.add_state(2, accepting=False)
    d.set_start(0)

    # on 'a' rotate mod 3
    d.add_transition(0, "a", 1)
    d.add_transition(1, "a", 2)
    d.add_transition(2, "a", 0)

    # on 'b' stay
    d.add_transition(0, "b", 0)
    d.add_transition(1, "b", 1)
    d.add_transition(2, "b", 2)

    return d


def describe():
    return "Words over {a,b} with number of 'a' divisible by 3."
