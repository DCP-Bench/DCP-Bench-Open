Print the 0-based indices of the winning set of cards (winning_cards) -> three slots, each one-hot over the card indices (sel[s][i]), exactly one card per slot
three cards -> each card in at most one slot: sum over s of sel[s][i] <= 1
the three cards must be distinct cards on the table -> covered by the one-card-per-slot and at-most-one-slot constraints
For each one of the four categories of features (color, number, shape, shading) the three cards must display that feature as either all the same, or all different -> for each feature and each value v of the instance domain: count of chosen cards with value v is at most 1 or at least 3 (Or of two PB comparisons; count of 2 is the only forbidden case)
objective -> satisfaction (no objective)
