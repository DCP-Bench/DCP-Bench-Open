# The card game Set: among the cards on the table find three that form a set,
# that is, for each of the four features (number, fill, colour, shape) the three
# cards either all show the same value or all show different values.
from hermax.model import Model


def build(instance):
    cards = instance["cards_data"]  # each card is [number, fill, colour, shape]
    n_cards = len(cards)
    n_features = 4

    m = Model()
    # winning_cards = the indices of the three chosen cards, all different
    winning_cards = m.int_vector("winning_cards", 3, 0, n_cards - 1)
    m &= winning_cards.all_different()

    for f in range(n_features):
        values = sorted({card[f] for card in cards})
        # shown[k] = the value of feature f on the k-th chosen card
        shown = m.int_vector(f"feature_{f}", 3, values[0], values[-1])
        for k in range(3):
            for c in range(n_cards):
                m &= (~(winning_cards[k] == c) | (shown[k] == cards[c][f]))
        # the three values are all equal or all different: if two of the cards
        # share a value, the third one shares it too
        for v in values:
            for a, b, c in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):
                m &= (~(shown[a] == v) | ~(shown[b] == v) | (shown[c] == v))

    return m, {"winning_cards": winning_cards}
