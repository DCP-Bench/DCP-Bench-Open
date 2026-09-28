"""Bin packing: put every item in one of the bins so that no bin holds more than its capacity."""
from docplex.mp.model import Model


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    items = range(len(weights))
    bins = range(instance["num_bins"])

    model = Model("bin_packing")

    # put[j, b] is 1 when item j goes into bin b.
    put = model.binary_var_matrix(items, bins, name="put")

    # Every item goes into exactly one bin.
    for j in items:
        model.add_constraint(model.sum(put[j, b] for b in bins) == 1, ctname=f"one_bin_{j}")

    # The items in a bin weigh no more than the bin's capacity.
    for b in bins:
        model.add_constraint(model.sum(weights[j] * put[j, b] for j in items) <= capacity,
                             ctname=f"capacity_{b}")

    # The bin of each item, 0-indexed, read back from the assignment.
    bin_of = [model.sum(b * put[j, b] for b in bins) for j in items]
    return model, {"bins": bin_of}
