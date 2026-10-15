"""Bin packing: assign each item to one of num_bins bins so that no bin exceeds its capacity.

Each item i has a one-hot assignment over the bins: x[i][b] is true when item i is in bin b.
"""

from paramita.modelling import Bool


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    # x[i][b] is true when item i is put in bin b
    x = [[Bool(f"x_{i}_{b}") for b in range(num_bins)] for i in range(n)]

    cons = []

    # every item is in exactly one bin
    for i in range(n):
        cons.append(sum(x[i]) == 1)

    # the total weight of the items in each bin does not exceed the capacity
    for b in range(num_bins):
        cons.append(sum(weights[i] * x[i][b] for i in range(n)) <= capacity)

    # symmetry breaking: bins are interchangeable, so number them in the order of their first item;
    # item i can then only use a bin with index at most i
    for i in range(n):
        for b in range(i + 1, num_bins):
            cons.append(~x[i][b])

    # the bin index of each item as an integer expression
    bins = [sum(b * x[i][b] for b in range(num_bins)) for i in range(n)]
    return cons, {"bins": bins}
