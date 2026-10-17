# Set (card game): the layout holds n cards, each a row of cards_data with four feature values in 1..3.
# Find three distinct cards that form a set, and output their 0-based indices as winning_cards.
# Satisfaction problem: no objective.
import mip


def build(instance):
    cards = instance["cards_data"]
    n = len(cards)
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Choosing the three cards: p[k][c] = 1 when card c is the k-th card of the set.
    p = [[model.add_var(f"p_{k}_{c}", var_type=mip.BINARY) for c in range(n)]
         for k in range(3)]
    # The output: the 0-based index of the k-th card, tied to its selection.
    w = [model.add_var(f"w_{k}", lb=0, ub=n - 1, var_type=mip.INTEGER)
         for k in range(3)]
    for k in range(3):
        # Exactly one card is the k-th card.
        model += mip.xsum(p[k]) == 1
        model += w[k] == mip.xsum(c * p[k][c] for c in range(n))

    # The three cards must be different cards: each card is picked at most once.
    for c in range(n):
        model += mip.xsum(p[k][c] for k in range(3)) <= 1

    # For each feature, the three cards must display that feature as either all the same or all
    # different. With the values 1..3 read as residues mod 3, three values are all the same or all
    # different exactly when their sum is 0 mod 3. So the sum of the feature over the three cards
    # equals 3 * t for an integer t.
    for f in range(4):
        t = model.add_var(f"t_{f}", lb=0, ub=3, var_type=mip.INTEGER)
        model += mip.xsum(cards[c][f] * p[k][c] for k in range(3) for c in range(n)) == 3 * t

    return model, {"winning_cards": w}
