"""
Converts a decision tree into a DFA.
Each node becomes a DFA state.
"""

from dfa import DFA


def tree_to_dfa(root):
    """
    Converts a decision tree to an equivalent DFA.
    """
    d = DFA()
    mapping = {}
    state_id = 0

    def assign(node):
        nonlocal state_id
        if node in mapping:
            return mapping[node]

        mapping[node] = state_id
        d.add_state(state_id, accepting=(node.value == 1))
        sid = state_id
        state_id += 1

        if node.value is not None:
            return sid

        left = assign(node.left)
        right = assign(node.right)

        # simple uniform transition behavior
        d.add_transition(sid, 'a', left)
        d.add_transition(sid, 'b', right)

        return sid

    root_id = assign(root)
    d.set_start(root_id)
    return d
