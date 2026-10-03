"""Set (card game): every card has four features (number, fill, color, shape), each with three
possible values. Three cards form a set if, for each feature, the three cards show either the
same value or three different values. Find a set among the cards on the table.

The model reports the indices of the three cards of the set.
"""
import pulp


def build(instance):
    cards = instance["cards_data"]  # each card is [number, fill, color, shape]
    # the possible values of each feature, in the order of the columns of a card
    feature_values = [instance["numbers"], instance["fills"],
                      instance["colors"], instance["shapes"]]
    n_cards = len(cards)

    problem = pulp.LpProblem("set_game", pulp.LpMinimize)  # satisfaction: no objective

    # choose[p][c] = 1 if the p-th card of the set is card c. Each of the three places holds one
    # card, and a card is used at most once (the three cards are different).
    choose = pulp.LpVariable.dicts("choose", (range(3), range(n_cards)), cat="Binary")
    winning_cards = [pulp.LpVariable(f"winning_{p}", 0, n_cards - 1, cat="Integer")
                     for p in range(3)]
    for p in range(3):
        problem += pulp.lpSum(choose[p][c] for c in range(n_cards)) == 1
        problem += winning_cards[p] == pulp.lpSum(c * choose[p][c] for c in range(n_cards))
    for c in range(n_cards):
        problem += pulp.lpSum(choose[p][c] for p in range(3)) <= 1

    # For each feature, the three cards show the same value or three different values. Let
    # shown be how many of the three cards show the value v. Then the same value means shown = 3
    # for one v, and different values mean shown = 1 for each of three values. What is excluded
    # is two cards showing one value and the third another: shown = 2. The count is written as
    # either 1 (one_card[v]) or 3 (all_cards[v]), or 0 when neither is chosen.
    for f, values in enumerate(feature_values):
        for v in values:
            shown = pulp.lpSum(choose[p][c] for p in range(3) for c in range(n_cards)
                               if cards[c][f] == v)
            one_card = pulp.LpVariable(f"one_card_{f}_{v}", cat="Binary")
            all_cards = pulp.LpVariable(f"all_cards_{f}_{v}", cat="Binary")
            problem += shown == one_card + 3 * all_cards
            problem += one_card + all_cards <= 1

    return problem, {"winning_cards": winning_cards}
