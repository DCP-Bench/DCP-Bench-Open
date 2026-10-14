"""Bowls and oranges: put m oranges in distinct bowls 1..n so that no three are evenly spaced."""
from docplex.mp.model import Model


def build(instance):
    n, m = instance["n"], instance["m"]

    model = Model("bowls_and_oranges")

    # x[i] is the bowl of the i-th orange, listed in ascending order; distinct
    # and ascending together mean strictly increasing.
    x = model.integer_var_list(m, 1, n, name="x")
    for i in range(1, m):
        model.add_constraint(x[i] >= x[i - 1] + 1, ctname=f"ascending_{i}")

    # For oranges A < B < C, the distance from A to B differs from that from B to C.
    for a in range(m):
        for b in range(a + 1, m):
            for c in range(b + 1, m):
                model.add(x[b] - x[a] != x[c] - x[b])

    return model, {"x": x}
