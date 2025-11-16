import random
from collections import defaultdict, deque


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

    def minimize(self):
        """
        Minimizes the DFA using Hopcroft's algorithm.
        Returns a new minimized DFA.
        """
        P = [set(self.accepting_states), self.states - set(self.accepting_states)]
        W = [set(self.accepting_states)]

        while W:
            A = W.pop()
            for c in self.alphabet:
                X = {q for q in self.states if self.step(q, c) in A}

                newP = []
                for Y in P:
                    i = X & Y
                    d = Y - X
                    if i and d:
                        newP.append(i)
                        newP.append(d)
                        if Y in W:
                            W.remove(Y)
                            W.append(i)
                            W.append(d)
                        else:
                            W.append(i if len(i) <= len(d) else d)
                    else:
                        newP.append(Y)
                P = newP

        # Build minimized DFA
        mapping = {}
        for i, block in enumerate(P):
            for s in block:
                mapping[s] = i

        new = DFA(self.alphabet)
        for old, new_id in mapping.items():
            new.add_state(new_id, old in self.accepting_states)

        new.set_start(mapping[self.start_state])

        for q in self.states:
            for a in self.alphabet:
                nxt = self.step(q, a)
                if nxt is not None:
                    new.add_transition(mapping[q], a, mapping[nxt])

        return new

    def product(self, other):
        """
        Builds the product automaton for equivalence checking.
        State (p,q) is accepting iff DFAs disagree on acceptance.
        """
        prod = DFA(self.alphabet)

        start = (self.start_state, other.start_state)
        prod.set_start(start)

        queue = deque([start])
        visited = set([start])

        while queue:
            s1, s2 = queue.popleft()

            disagree = (s1 in self.accepting_states) != (s2 in other.accepting_states)
            prod.add_state((s1, s2), accepting=disagree)

            for a in self.alphabet:
                n1 = self.step(s1, a)
                n2 = other.step(s2, a)
                if n1 is None or n2 is None:
                    continue
                nxt = (n1, n2)
                prod.add_transition((s1, s2), a, nxt)
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        return prod

    def is_equivalent(self, other):
        """
        Two DFAs are equivalent if in the product automaton
        there is NO accepting state (disagreement).
        """
        prod = self.product(other)

        queue = deque([prod.start_state])
        visited = set([prod.start_state])

        while queue:
            q = queue.popleft()
            if q in prod.accepting_states:  # disagreement
                return False
            for a in prod.alphabet:
                nxt = prod.step(q, a)
                if nxt and nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        return True
