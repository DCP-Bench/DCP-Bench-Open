"""Set card game: choose three of the cards on the table that form a set; print their 0-based indices (winning_cards)."""
from paramita.modelling import Bool, If

SLOTS = 3  # the three cards of the set
FEATURES = ["numbers", "fills", "colors", "shapes"]  # cards_data columns: number, fill, color, shape


def build(instance):
    cards = instance["cards_data"]
    n = len(cards)
    # sel[s][i] = 1 if card i is the s-th card of the set (one-hot over the cards on the table)
    sel = [[Bool(f"slot_{s}_card_{i}") for i in range(n)] for s in range(SLOTS)]
    cons = []

    # each slot holds exactly one card
    for s in range(SLOTS):
        cons.append(sum(sel[s]) == 1)

    # the three cards are different cards: each card fills at most one slot
    for i in range(n):
        cons.append(sum(sel[s][i] for s in range(SLOTS)) <= 1)

    # for each feature, the three cards are all the same or all different:
    # no feature value may be shown by exactly two of the three cards
    for f, field in enumerate(FEATURES):
        for v in instance[field]:
            holders = [i for i in range(n) if cards[i][f] == v]
            count = sum(sel[s][i] for i in holders for s in range(SLOTS))
            cons.append((count <= 1) | (count >= 3))

    # print the 0-based indices of the three cards
    outputs = {"winning_cards": [sum(i * sel[s][i] for i in range(n)) for s in range(SLOTS)]}
    return cons, outputs
