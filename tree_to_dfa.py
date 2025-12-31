"""
Converts a decision tree into a DFA.
  - A DFA state encodes all *prefix information* needed to reconstruct the
    same feature vector as extract_features(word) would produce.
  - Acceptance of a DFA state is decided by evaluating the decision tree on
    the reconstructed feature vector.
  - The DFA is built by exploring all reachable prefixes up to max_len.

Conceptually, this construction treats prefixes as automaton states.
The starting point is a prefix-tree (trie / prefix tree acceptor), where
each node corresponds to a prefix and each outgoing edge corresponds to
reading the next symbol. Prefixes that are indistinguishable with respect
to the decision tree's feature representation are mapped to the same DFA
state. Acceptance is determined by the classifier rather than by explicit
membership in a sample set.

References:
  -Prefix Tree Acceptors (PTA) and prefixes as DFA states:
    https://en.wikipedia.org/wiki/Prefix_tree_acceptor

  -Tries interpreted as deterministic finite automata:
    https://en.wikipedia.org/wiki/Trie

  -Decision trees over finite domains defining regular languages:
    https://cs.stackexchange.com/questions/34642/decision-tree-to-automaton

  -Prefix-tree-based construction:
    https://rahul.gopinath.org/post/2021/10/08/learn-regular/

  -Practical DFA representations using transition tables in Python:
    https://stackoverflow.com/questions/42193173/designing-and-implementing-a-dfa-in-python
"""


from collections import deque
from dfa import DFA
from decision_tree import Node


def initial_primitive_state():
    """
    Primitive state describes what we know about the prefix:
        length, a_count, b_count,
        first_char, last_char,
        has_aa, has_ab, has_ba, has_bb
    """
    return {
        "length": 0,
        "a_count": 0,
        "b_count": 0,
        "first_char": None,
        "prev_char": None,
        "last_char": None,
        "has_aa": 0,
        "has_ab": 0,
        "has_ba": 0,
        "has_bb": 0,
    }


def update_primitive_state(state, symbol):
    """
    Updates primitive state after reading one symbol ('a' or 'b').
    """
    new = dict(state)
    length = new["length"]
    last = new["last_char"]

    # length
    length += 1
    new["length"] = length

    # first_char
    if length == 1:
        new["first_char"] = symbol

    # counts
    if symbol == "a":
        new["a_count"] += 1
    else:
        new["b_count"] += 1

    # previous character (needed for suffix bigram features)
    new["prev_char"] = last

    # patterns based on (last_char, symbol)
    if last is not None:
        pair = last + symbol
        if pair == "aa":
            new["has_aa"] = 1
        elif pair == "ab":
            new["has_ab"] = 1
        elif pair == "ba":
            new["has_ba"] = 1
        elif pair == "bb":
            new["has_bb"] = 1

    # last_char
    new["last_char"] = symbol

    return new

def features_from_primitive_state(state):
    """
    Reconstructs the same feature dictionary that extract_features(word)
    would produce, but using only primitive state (no full word needed).
    """
    length = state["length"]
    a_count = state["a_count"]
    b_count = state["b_count"]
    first_char = state["first_char"]
    prev_char = state["prev_char"]
    last_char = state["last_char"]

    features = {}

    # length & mods
    features["length"] = length
    features["length_mod2"] = length % 2
    features["length_mod3"] = length % 3

    # counts & parities
    features["a_count"] = a_count
    features["b_count"] = b_count
    features["a_parity"] = a_count % 2
    features["b_parity"] = b_count % 2
    features["a_mod3"] = a_count % 3
    features["b_mod3"] = b_count % 3

    # start/end
    features["starts_with_a"] = 1 if first_char == "a" else 0
    features["starts_with_b"] = 1 if first_char == "b" else 0
    features["ends_with_a"] = 1 if last_char == "a" else 0
    features["ends_with_b"] = 1 if last_char == "b" else 0

    # patterns
    features["has_aa"] = state["has_aa"]
    features["has_ab"] = state["has_ab"]
    features["has_ba"] = state["has_ba"]
    features["has_bb"] = state["has_bb"]

    # suffix bigram flags
    if prev_char is None or last_char is None:
        features["ends_with_aa"] = 0
        features["ends_with_ab"] = 0
        features["ends_with_ba"] = 0
        features["ends_with_bb"] = 0
    else:
        last2 = prev_char + last_char
        features["ends_with_aa"] = 1 if last2 == "aa" else 0
        features["ends_with_ab"] = 1 if last2 == "ab" else 0
        features["ends_with_ba"] = 1 if last2 == "ba" else 0
        features["ends_with_bb"] = 1 if last2 == "bb" else 0

    # relations between counts
    features["more_a_than_b"] = 1 if a_count > b_count else 0
    features["equal_a_b"] = 1 if a_count == b_count else 0

    return features


def predict_tree(node, features):
    """
    Evaluates the decision tree on a feature dictionary.
    """
    while True:
        # leaf?
        if node.value is not None:
            return bool(node.value)

        # internal node
        val = features[node.feature]
        if val <= node.threshold:
            node = node.left
        else:
            node = node.right



def primitive_key(state):
    """
    Converts primitive state dict into a hashable key for state_map.
    """
    return (
        state["length"],
        state["a_count"],
        state["b_count"],
        state["first_char"],
        state["prev_char"],
        state["last_char"],
        state["has_aa"],
        state["has_ab"],
        state["has_ba"],
        state["has_bb"],
    )


def tree_to_dfa(root, max_len=10, alphabet=("a", "b")):
    """
    Builds a DFA that simulates the decision tree on prefixes
    up to given max_len.

    State of DFA encodes:
      - primitive prefix statistics
    Acceptance = decision_tree(features_from_primitive_state(state)).
    """
    dfa = DFA(alphabet=alphabet)

    state_map = {}  # primitive_key -> state_id
    queue = deque()
    next_id = 0

    def ensure_state(state):
        nonlocal next_id
        key = primitive_key(state)
        if key in state_map:
            return state_map[key]

        sid = next_id
        next_id += 1
        state_map[key] = sid

        # compute features and mark accepting
        features = features_from_primitive_state(state)
        is_accepting = predict_tree(root, features)
        dfa.add_state(sid, accepting=is_accepting)

        queue.append(state)
        return sid

    # initial state: empty prefix
    init_prim = initial_primitive_state()
    start_id = ensure_state(init_prim)
    dfa.set_start(start_id)

    # BFS over reachable primitive states (up to max_len)
    while queue:
        state = queue.popleft()
        sid = state_map[primitive_key(state)]

        # do not expand beyond max_len (training/test generator uses this bound)
        if state["length"] >= max_len:
            continue

        for sym in alphabet:
            new_state = update_primitive_state(state, sym)
            nid = ensure_state(new_state)
            dfa.add_transition(sid, sym, nid)

    return dfa
