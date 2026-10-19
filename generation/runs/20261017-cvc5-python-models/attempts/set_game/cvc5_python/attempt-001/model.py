# Set card game: choose three distinct cards from the layout so that, for each of the four
# features (number, fill, color, shape), the three cards show that feature either all the same
# or all different. Each card is cards_data[i] = [number, fill, color, shape], values 1..3.
# Output winning_cards: the 0-based indices of the three cards.
import cvc5.pythonic as cz


def build(instance):
    cards = instance["cards_data"]
    n = len(cards)
    idx = [cz.Int(f"card_{p}") for p in range(3)]

    # Card indices must be valid positions in this layout.
    # Three distinct cards are the winning set.
    constraints = [cz.Distinct(idx)]
    for i in idx:
        constraints.append(i >= 0)
        constraints.append(i <= n - 1)

    def feature_of(card_var, f):
        # Value of feature f on the card whose index is card_var, read from this instance's data.
        expr = cards[n - 1][f]
        for k in range(n - 2, -1, -1):
            expr = cz.If(card_var == k, cards[k][f], expr)
        return expr

    # Each feature: the three cards are all the same, or all different.
    for f in range(4):
        vals = [feature_of(i, f) for i in idx]
        constraints.append(
            cz.Or(
                cz.And(vals[0] == vals[1], vals[1] == vals[2]),
                cz.Distinct(vals),
            )
        )

    return constraints, {"winning_cards": idx}
