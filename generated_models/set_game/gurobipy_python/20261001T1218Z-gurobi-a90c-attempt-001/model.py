"""Set game: find three different cards whose number, fill, colour and shape are each all equal or all different."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    cards = instance["cards_data"]   # each card is [number, fill, color, shape]
    n_cards = len(cards)
    slots = range(3)
    card_ids = range(n_cards)

    model = gp.Model("set_game")

    # pick[k, c] is 1 when the k-th winning card is card c.
    pick = model.addVars(slots, card_ids, vtype=GRB.BINARY, name="pick")
    for k in slots:
        model.addConstr(pick.sum(k, "*") == 1, name=f"one_card[{k}]")

    # The three winning cards are all different.
    for c in card_ids:
        model.addConstr(pick.sum("*", c) <= 1, name=f"distinct[{c}]")

    # For every feature the three values are all equal or all different, which for
    # three cards means no value is shown by exactly two of them: the number of
    # chosen cards showing a value is 0, 1 or 3 (one * single + 3 * triple).
    for f in range(len(cards[0])):
        for v in sorted({card[f] for card in cards}):
            shown = gp.quicksum(pick[k, c] for k in slots for c in card_ids if cards[c][f] == v)
            single = model.addVar(vtype=GRB.BINARY, name=f"single[{f},{v}]")
            triple = model.addVar(vtype=GRB.BINARY, name=f"triple[{f},{v}]")
            model.addConstr(single + triple <= 1, name=f"not_two[{f},{v}]")
            model.addConstr(shown == single + 3 * triple, name=f"all_or_none[{f},{v}]")

    # The 0-based indices of the winning cards.
    return model, {"winning_cards": [gp.quicksum(c * pick[k, c] for c in card_ids) for k in slots]}
