# The card game Set: among the cards on the table find three that form a set,
# that is, for each of the four features (number, fill, colour, shape) the three
# cards either all show the same value or all show different values.
from exact import Exact


def build(instance):
    cards = instance["cards_data"]  # each card is [number, fill, colour, shape]
    n_cards = len(cards)
    n_features = 4

    solver = Exact()
    # chosen[k][c] is 1 when the k-th chosen card is card c
    chosen = [[f"chosen_{k}_{c}" for c in range(n_cards)] for k in range(3)]
    winning_cards = [f"winning_{k}" for k in range(3)]
    for k in range(3):
        solver.addVariable(winning_cards[k], 0, n_cards - 1)
        for name in chosen[k]:
            solver.addVariable(name, 0, 1)
        # each chosen position holds exactly one card, and winning_cards[k] is its index
        solver.addConstraint([(1, name) for name in chosen[k]], True, 1, True, 1)
        solver.addConstraint([(c, chosen[k][c]) for c in range(1, n_cards)] + [(-1, winning_cards[k])],
                             True, 0, True, 0)
    # the three chosen cards are different
    for c in range(n_cards):
        solver.addConstraint([(1, chosen[k][c]) for k in range(3)], False, 0, True, 1)

    for f in range(n_features):
        for v in sorted({card[f] for card in cards}):
            # shows[k] is 1 when the k-th chosen card has value v for feature f
            shows = []
            for k in range(3):
                name = f"shows_{f}_{v}_{k}"
                solver.addVariable(name, 0, 1)
                solver.addConstraint([(1, name)] + [(-1, chosen[k][c]) for c in range(n_cards) if cards[c][f] == v],
                                     True, 0, True, 0)
                shows.append(name)
            # the three values are all equal or all different: if two of the cards
            # show v, the third shows it too
            for a, b, c in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):
                solver.addConstraint([(1, shows[a]), (1, shows[b]), (-1, shows[c])], False, 0, True, 1)

    return solver, {"winning_cards": winning_cards}
