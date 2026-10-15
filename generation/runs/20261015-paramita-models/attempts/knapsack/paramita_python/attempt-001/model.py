# Knapsack (0-1): a hiker chooses which items to put in the backpack.
# Each item is taken or not; the chosen items must fit the weight capacity,
# and the total value of the chosen items is maximised.
# No integer variables are needed: the objective and the capacity are
# linear sums over the item Bools (weights and values are small).

from paramita.modelling import Bool


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    # x[i] = 1 if item i is put in the backpack
    x = [Bool(f"x_{i}") for i in range(n)]

    cons = []
    # the total weight of the chosen items must not exceed the weight capacity
    cons.append(sum(weights[i] * x[i] for i in range(n)) <= capacity)

    # the objective is the total value of the chosen items
    total_value = sum(values[i] * x[i] for i in range(n))

    return cons, {"x": x}, ("maximize", total_value)
