"""Eighteen-hole golf: give each of 18 holes a length of 3, 4 or 5 so that the course has a
total length of 72.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the number of holes, the allowed lengths and the
    # total come from the statement.
    num_holes = 18
    total_length = 72

    model = Model("eighteen_hole_golf")

    # Each hole has length 3, 4 or 5.
    holes = [model.integer_var(3, 5, name=f"hole_{h}") for h in range(num_holes)]

    # The lengths add up to the course total.
    model.add_constraint(model.sum(holes) == total_length)

    return model, {"holes": holes}
