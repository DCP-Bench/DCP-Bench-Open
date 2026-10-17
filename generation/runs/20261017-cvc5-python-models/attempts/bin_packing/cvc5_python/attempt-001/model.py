# Bin packing: assign each item to one of a number of bins of fixed capacity so
# that the total weight of the items in each bin does not exceed the capacity.
# bins[k] is the 0-based bin of item k.

import cvc5.pythonic as cz


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]

    n_items = len(weights)

    # Each item is assigned to one bin, numbered 0 to num_bins - 1.
    bins = [cz.Int(f"bin_{k}") for k in range(n_items)]
    constraints = []
    for k in range(n_items):
        constraints.append(bins[k] >= 0)
        constraints.append(bins[k] <= num_bins - 1)

    # The total weight of the items in each bin does not exceed the bin capacity.
    for b in range(num_bins):
        constraints.append(
            cz.Sum([cz.If(bins[k] == b, weights[k], 0) for k in range(n_items)]) <= capacity
        )

    outputs = {"bins": bins}
    return constraints, outputs
