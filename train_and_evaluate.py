"""
Full training & evaluation pipeline.
"""

from generator import random_word_generator, even_a_dfa, label_words
from decision_tree import extract_features, build_tree
from tree_to_dfa import tree_to_dfa


def run():
    gold = even_a_dfa()

    train_words = random_word_generator(200)
    test_words = random_word_generator(200)

    labeled = label_words(gold, train_words)

    data = [(extract_features(w), y) for w, y in labeled]
    tree = build_tree(data)

    learned_dfa = tree_to_dfa(tree).minimize()

    # Accuracy
    correct = sum(1 for w in test_words
                  if learned_dfa.accepts(w) == gold.accepts(w))
    accuracy = correct / len(test_words)

    print("Accuracy:", accuracy)
    print("Equivalent:", learned_dfa.is_equivalent(gold))


if __name__ == "__main__":
    run()
