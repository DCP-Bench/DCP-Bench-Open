from pychoco.model import Model


def build(instance):
    """Bin packing: assign each item to a bin without overloading any bin."""
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    model = Model()
    bins = [model.intvar(0, num_bins - 1, name=f"bin{j}") for j in range(n)]

    # The reference ranges its capacity constraint over the item count rather
    # than the bin count; no item can land outside 0..num_bins-1, so the extra
    # indices constrain nothing and only the real bins are posted here.
    for b in range(num_bins):
        here = [model.arithm(bins[j], "=", b).reify() for j in range(n)]
        model.scalar(here, weights, "<=", capacity).post()

    return model, {"bins": bins}
