"""Candies: give every child at least one candy, more than any lower-rated neighbour, using as few candies as possible."""
from docplex.mp.model import Model


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    model = Model("candies")

    # x[i] is the candies child i gets; the reference model declares 1..n.
    x = model.integer_var_list(n, 1, n, name="x")

    # Of two neighbours, the one with the higher rating gets more candies.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            model.add_constraint(x[i - 1] >= x[i] + 1, ctname=f"neighbours_{i}")
        elif ratings[i - 1] < ratings[i]:
            model.add_constraint(x[i - 1] + 1 <= x[i], ctname=f"neighbours_{i}")

    # Minimise the total number of candies z.
    z = model.sum(x)
    model.minimize(z)

    return model, {"z": z, "x": x}
