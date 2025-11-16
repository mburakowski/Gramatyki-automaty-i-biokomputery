"""
Simple binary decision tree for word classification.
"""

class Node:
    """
    Tree node.
    Stores: feature name OR final value (0/1).
    """
    def __init__(self, feature=None, left=None, right=None, value=None):
        self.feature = feature
        self.left = left
        self.right = right
        self.value = value


def extract_features(word):
    """
    Extracts binary features from the given word.
    """
    return {
        "ends_a": word.endswith("a"),
        "has_bb": "bb" in word,
        "even_len": len(word) % 2 == 0,
        "more_a": word.count("a") > word.count("b")
    }


# -----------------------
# ENTROPY & TREE BUILDING
# -----------------------

from math import log2


def entropy(labels):
    if not labels:
        return 0
    p = sum(labels) / len(labels)
    if p == 0 or p == 1:
        return 0
    return -p * log2(p) - (1 - p) * log2(1 - p)


def best_split(data):
    """
    Finds best feature split.
    """
    features = data[0][0].keys()
    base_entropy = entropy([l for _, l in data])

    best_gain = 0
    best_feature = None
    best_left = None
    best_right = None

    for f in features:
        left = [(x, y) for x, y in data if x[f]]
        right = [(x, y) for x, y in data if not x[f]]

        if not left or not right:
            continue

        gain = base_entropy - (
            len(left) / len(data) * entropy([l for _, l in left]) +
            len(right) / len(data) * entropy([l for _, l in right])
        )

        if gain > best_gain:
            best_gain = gain
            best_feature = f
            best_left = left
            best_right = right

    return best_feature, best_left, best_right


def build_tree(data):
    """
    Recursively builds the decision tree.
    """
    labels = [l for _, l in data]
    if all(l == 0 for l in labels):
        return Node(value=0)
    if all(l == 1 for l in labels):
        return Node(value=1)

    feature, left_data, right_data = best_split(data)
    if feature is None:
        return Node(value=round(sum(labels) / len(labels)))

    left = build_tree(left_data)
    right = build_tree(right_data)
    return Node(feature=feature, left=left, right=right)
