# The card game Set: among the cards on the table find three that form a set,
# that is, for each of the four features (number, fill, colour, shape) the three
# cards either all show the same value or all show different values.
import z3


def build(instance):
    cards = instance["cards_data"]  # each card is [number, fill, colour, shape]
    n_cards = len(cards)
    n_features = 4

    solver = z3.Solver()

    # winning_cards = the indices of the three chosen cards, all different
    winning_cards = [z3.Int(f"winning_{k}") for k in range(3)]
    for index in winning_cards:
        solver.add(index >= 0, index < n_cards)
    solver.add(z3.Distinct(winning_cards))

    def feature_of(index, f):
        """The value of feature f on the card with the given index: Z3 has no
        element constraint, so it is an If chain over the cards."""
        value = cards[n_cards - 1][f]
        for k in range(n_cards - 2, -1, -1):
            value = z3.If(index == k, cards[k][f], value)
        return value

    for f in range(n_features):
        a, b, c = (feature_of(index, f) for index in winning_cards)
        # the three values are either all equal or all different
        solver.add(z3.Or(z3.And(a == b, b == c), z3.Distinct(a, b, c)))

    return solver, {"winning_cards": winning_cards}
