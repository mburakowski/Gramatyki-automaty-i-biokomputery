import random
from collections import defaultdict


class DFA:
    """
    Implementation of a Deterministic Finite Automata (DFA).
    Enables:
        adding states,
        setting start state,
        defining transitions,
        setting states as accepting,
        checking the acceptance of the word

    Contains:
        states - a set of states,
        start_state - starting state
        accepting_states - a set of accepting states
        transitions - a dictionary: transitions[q][symbol] -> q_next
    """
    def __init__(self, alphabet=('a', 'b')):
        self.alphabet = tuple(alphabet)
        self.states = set()
        self.start_state = None
        self.accepting_states = set()
        # transition dictionary
        self.transitions = defaultdict(dict)

    def add_state(self, state, accepting_states=False):
        """
        Adds a new state, can mark a state as accepting
        :param state:
        :param accepting_states:
        :return:
        """
        self.states.add(state)
        if accepting_states:
            self.accepting_states.add(state)

    def set_start(self, state):
        """
        Sets a starting state of an automaton
        :param state:
        :return:
        """
        self.states.add(state)
        self.start_state = state

    def set_accepting_state(self, state, val=True):
        """
        Sets a state as accepting or not
        :param state:
        :param val:
        :return:
        """
        if val:
            self.accepting_states.add(state)
        else:
            self.accepting_states.discard(state)

    def add_transition(self, q_old, symbol, q_new):
        """
        Adds a deterministic transition: q_old -> symbol -> q_new
        Error if a symbol does not belong to the alphabet
        :param q_old:
        :param symbol:
        :param q_new:
        :return:
        """
        if symbol not in self.alphabet:
            raise ValueError(f"Symbol {symbol} does not belong to the alphabet")
        self.states.add(q_old)
        self.states.add(q_new)
        self.transitions[q_old][symbol] = q_new

    def step(self, state, symbol):
        """
        Transition function
        :param state:
        :param symbol:
        :return: returns state from symbol
        """
        return self.transitions.get(state, {}).get(symbol, None)

    def accepts(self, word):
        """
        Accepting function.
        Checks if the automaton accepts given word.
        Goes through dfa step by step - if any transition is missing, the word is rejected
        :param word:
        :return:
        """
        s = self.start_state
        for a in word:
            s = self.step(s, a)
            # if transition is missing
            if s is None:
                return False
            return s in self.accepting_states

    def visualise(self):
        """
        Returns a visual (text) representation of the dfa:
            list of states,
            starting state,
            list of accepting states,
            transitions in format q_old -> symbol -> _new
        :return: (string) description of the dfa
        """
        lines = [f"States: {sorted(self.states)}", f"Start: {self.start_state}",
                 f"Accepting states: {sorted(self.accepting_states)}", "Transitions:"]

        for state in sorted(self.states):
            for symbol in self.alphabet:
                if symbol in self.transitions.get(state, {}):
                    next_state = self.transitions[state][symbol]
                    lines.append(f"  {state} -{symbol}-> {next_state}")

        return "\n".join(lines)


def random_word_generator(n, min_len=1, max_len=10, alphabet=('a','b')):
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
        length = random.randint(min_len, max_len)
        word = "".join(random.choice(alphabet) for _ in range(length))
        words.append(word)
    return words
