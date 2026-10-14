"""Coin set: the fewest coins from which every amount below the maximum can be paid exactly."""
from docplex.mp.model import Model


def build(instance):
    denominations = instance["denominations"]
    top = instance["max_amount_to_pay"]
    kinds = range(len(denominations))
    amounts = range(1, top)

    model = Model("coin3_application")

    # x[i] is how many coins of denomination i are in the set; the reference
    # model allows 0..top for each, and 0..top for their total.
    x = model.integer_var_list(len(denominations), 0, top, name="x")
    model.add_constraint(model.sum(x) <= top, ctname="total_coins")

    # For every amount from 1 to top - 1, some selection of the coins in the set
    # pays it exactly: pay[j, i] coins of denomination i, never more than x[i].
    pay = model.integer_var_matrix(amounts, kinds, 0, top, name="pay")
    for j in amounts:
        model.add_constraint(model.sum(denominations[i] * pay[j, i] for i in kinds) == j, ctname=f"pays_{j}")
        for i in kinds:
            model.add_constraint(pay[j, i] <= x[i], ctname=f"from_set_{j}_{i}")

    # Minimise the number of coins in the set.
    model.minimize(model.sum(x))

    return model, {"x": x}
