"""Set card game: among the cards on the table, find three different cards that form a set, meaning
that for each feature (number, fill, color, shape) the three cards show either all the same value
or all different values.

The model reports the 0-based indices of the three winning cards.
"""
from docplex.mp.model import Model


def build(instance):
    cards = instance["cards_data"]  # each card is [number, fill, color, shape]
    n_cards = len(cards)
    n_features = len(cards[0]) if cards else 0
    slots = range(3)

    model = Model("set_game")

    # pick[k, i] = 1 when the k-th winning card is card i; every slot holds exactly one card.
    pick = {(k, i): model.binary_var(name=f"pick_{k}_{i}") for k in slots for i in range(n_cards)}
    for k in slots:
        model.add_constraint(model.sum(pick[k, i] for i in range(n_cards)) == 1)

    # The three winning cards are different cards.
    for i in range(n_cards):
        model.add_constraint(model.sum(pick[k, i] for k in slots) <= 1)

    # For every feature, the three cards show all the same value or all different values. With
    # three cards that is: no value of the feature appears on exactly two of them, i.e. each
    # value appears on 0, 1 or 3 cards. once[f, v] and thrice[f, v] say which.
    for f in range(n_features):
        for v in sorted({card[f] for card in cards}):
            showing = model.sum(pick[k, i] for k in slots for i in range(n_cards) if cards[i][f] == v)
            once = model.binary_var(name=f"once_{f}_{v}")
            thrice = model.binary_var(name=f"thrice_{f}_{v}")
            model.add_constraint(once + thrice <= 1)
            model.add_constraint(showing == once + 3 * thrice)

    winning_cards = [model.sum(i * pick[k, i] for i in range(n_cards)) for k in slots]
    return model, {"winning_cards": winning_cards}
