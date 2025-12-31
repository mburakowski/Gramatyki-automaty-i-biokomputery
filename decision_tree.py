import math
from typing import Callable, Dict, List, Optional

class Node:
    def __init__(self, feature=None, threshold=None,
                 left=None, right=None, value=None):
        """
        Binary decision tree node.

        feature   – feature name (string)
        threshold – split threshold (e.g. 0/1)
        left      – subtree for feature <= threshold
        right     – subtree for feature > threshold
        value     – leaf value (True/False) if this node is a leaf
        """
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    def is_leaf(self):
        """Returns True if this node is a leaf."""
        return self.value is not None


def extract_features(word: str) -> Dict[str, int]:
    """Extracts binary and numerical features from a word.

    Designed specifically for regular language induction and DFA learning.
    Returns a dictionary mapping feature names to integer values.
    """

    features: Dict[str, int] = {}

    # Basic features
    features['length'] = len(word)
    features['length_mod2'] = len(word) % 2
    features['length_mod3'] = len(word) % 3

    # Symbol counts
    a_count = word.count('a')
    b_count = word.count('b')
    features['a_count'] = a_count
    features['b_count'] = b_count
    features['a_parity'] = a_count % 2
    features['b_parity'] = b_count % 2
    features['a_mod3'] = a_count % 3
    features['b_mod3'] = b_count % 3

    # Positional features
    features['starts_with_a'] = 1 if word.startswith('a') else 0
    features['starts_with_b'] = 1 if word.startswith('b') else 0
    features['ends_with_a'] = 1 if word.endswith('a') else 0
    features['ends_with_b'] = 1 if word.endswith('b') else 0

    # Substring pattern features
    features['has_aa'] = 1 if 'aa' in word else 0
    features['has_ab'] = 1 if 'ab' in word else 0
    features['has_ba'] = 1 if 'ba' in word else 0
    features['has_bb'] = 1 if 'bb' in word else 0

    # Suffix bigram features
    features['ends_with_aa'] = 1 if word.endswith('aa') else 0
    features['ends_with_ab'] = 1 if word.endswith('ab') else 0
    features['ends_with_ba'] = 1 if word.endswith('ba') else 0
    features['ends_with_bb'] = 1 if word.endswith('bb') else 0

    # Content comparison features
    features['more_a_than_b'] = 1 if a_count > b_count else 0
    features['equal_a_b'] = 1 if a_count == b_count else 0

    return features


# Entropy and decision tree construction
def entropy(labels: List[bool]) -> float:
    """Computes entropy of a set of boolean labels (True/False)."""
    if len(labels) == 0:
        return 0.0

    p_true = sum(labels) / len(labels)
    p_false = 1 - p_true

    result = 0.0
    if p_true > 0:
        result -= p_true * math.log2(p_true)
    if p_false > 0:
        result -= p_false * math.log2(p_false)

    return result


def best_split(features_list: List[Dict[str, int]], labels: List[bool]):
    """Finds the best split (feature, threshold) using information gain.

    All features are evaluated.
    Thresholds are usually in {0, 1}, but arbitrary numeric values are supported.
    """

    best_gain = -1
    best_feature = None
    best_threshold = None

    all_features = features_list[0].keys()

    for feature in all_features:
        values = [f[feature] for f in features_list]
        thresholds = sorted(set(values))

        for thr in thresholds:
            left_labels = [labels[i] for i in range(len(labels)) if values[i] <= thr]
            right_labels = [labels[i] for i in range(len(labels)) if values[i] > thr]

            if len(left_labels) == 0 or len(right_labels) == 0:
                continue

            left_entropy = entropy(left_labels)
            right_entropy = entropy(right_labels)

            p_left = len(left_labels) / len(labels)
            p_right = 1 - p_left

            gain = entropy(labels) - (p_left * left_entropy + p_right * right_entropy)

            if gain > best_gain:
                best_gain = gain
                best_feature = feature
                best_threshold = thr

    return best_feature, best_threshold


def build_tree(
    words: List[str],
    labels: List[bool],
    max_depth: int = 12,
    depth: int = 0,
    feature_fn: Optional[Callable[[str], Dict[str, int]]] = None,
) -> Node:
    """Builds a binary decision tree.

    words      – list of input words
    labels     – corresponding True/False labels
    feature_fn – feature extraction function (default: extract_features)
    """

    if feature_fn is None:
        feature_fn = extract_features

    # All labels identical → create a leaf
    if all(l is True for l in labels):
        return Node(value=True)
    if all(l is False for l in labels):
        return Node(value=False)

    # Maximum depth reached → majority leaf
    if depth >= max_depth:
        majority = sum(labels) >= len(labels) / 2
        return Node(value=majority)

    # Compute feature vectors
    features_list = [feature_fn(w) for w in words]

    # Find the best split
    feature, threshold = best_split(features_list, labels)

    # No valid split → majority leaf
    if feature is None:
        majority = sum(labels) >= len(labels) / 2
        return Node(value=majority)

    # Partition the dataset
    left_words: List[str] = []
    left_labels: List[bool] = []
    right_words: List[str] = []
    right_labels: List[bool] = []

    for i in range(len(words)):
        if features_list[i][feature] <= threshold:
            left_words.append(words[i])
            left_labels.append(labels[i])
        else:
            right_words.append(words[i])
            right_labels.append(labels[i])

    # Recursive construction
    left_child = build_tree(left_words, left_labels, max_depth, depth + 1, feature_fn=feature_fn)
    right_child = build_tree(right_words, right_labels, max_depth, depth + 1, feature_fn=feature_fn)

    return Node(feature=feature, threshold=threshold, left=left_child, right=right_child)


def predict_tree(node: Node, features: Dict[str, int]) -> bool:
    """Evaluates the decision tree on a given feature dictionary."""
    while True:
        if node.value is not None:
            return bool(node.value)

        val = features[node.feature]
        if val <= node.threshold:
            node = node.left
        else:
            node = node.right
