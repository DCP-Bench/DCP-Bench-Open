"""0-1 knapsack: choose which items a hiker packs so that the total value is as large as possible
without the total weight exceeding the backpack's capacity.

The model reports, for each item, whether it is packed.
"""
from docplex.mp.model import Model


def build(instance):
    values = instance["values"]      # value of each item
    weights = instance["weights"]    # weight of each item
    capacity = instance["capacity"]  # weight the backpack can carry
    items = range(len(values))

    model = Model("knapsack")

    # x[i] = 1 if item i goes into the backpack
    x = [model.binary_var(name=f"x_{i}") for i in items]

    # The packed items must not weigh more than the capacity.
    model.add_constraint(model.dot(x, weights) <= capacity)

    # Maximize the total value of the packed items.
    model.maximize(model.dot(x, values))

    return model, {"x": x}
