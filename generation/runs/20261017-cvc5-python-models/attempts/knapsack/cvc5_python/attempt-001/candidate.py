# 0-1 knapsack: a hiker chooses which items to take in a backpack.
# Each item has a value and a weight. Maximise the total value of the items taken
# without exceeding the weight capacity. Output x[i] is True when item i is taken.

import cvc5.pythonic as cz


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    x = [cz.Bool(f"x{i}") for i in range(n)]

    # The total weight of the items taken must not exceed the weight capacity of the backpack.
    total_weight = cz.Sum([cz.If(x[i], weights[i], 0) for i in range(n)])
    constraints = [total_weight <= capacity]

    # Maximise the total value of the items in the backpack.
    total_value = cz.Sum([cz.If(x[i], values[i], 0) for i in range(n)])

    return constraints, {"x": x}, ("maximize", total_value)
