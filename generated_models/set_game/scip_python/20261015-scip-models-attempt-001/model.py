# Set game: choose three of the 12 cards that form a set (every feature all same or all different).
from itertools import combinations

from pyscipopt import Model, quicksum


def build(instance):
    # each card is [number, fill, color, shape], with feature values 1, 2, 3 (instance data)
    cards = instance["cards_data"]
    n = len(cards)
    nfeat = len(cards[0])

    m = Model()
    triples = list(combinations(range(n), 3))

    # one binary per candidate triple of cards: x[t] = 1 if the triple is the winning set
    x = {t: m.addVar(name=f"x_{t[0]}_{t[1]}_{t[2]}", vtype="B") for t in triples}
    # exactly one winning set
    m.addCons(quicksum(x[t] for t in triples) == 1)

    # a set: for each feature, the three values are all the same or all different.
    # With values 1, 2, 3 this holds exactly when the three values sum to a multiple of 3
    # (sums 3, 6, 9 are all-same or all-different; the other multisets give 4, 5, 7, 8).
    # The sum S is a constant from the instance; q = S / 3 is an integer variable that
    # only has to exist when the triple is the winning set.
    for t in triples:
        for f in range(nfeat):
            S = sum(cards[c][f] for c in t)
            q = m.addVar(name=f"q_{t[0]}_{t[1]}_{t[2]}_{f}", vtype="I", lb=1, ub=3)
            # the three cards agree or differ on feature f (the winning set only)
            m.addConsIndicator(3 * q - S <= 0, binvar=x[t])
            m.addConsIndicator(3 * q - S >= 0, binvar=x[t])

    # the output gives the three card indices of the winning set (0-based)
    winning_cards = [
        quicksum(t[p] * x[t] for t in triples)
        for p in range(3)
    ]
    return m, {"winning_cards": winning_cards}
