# Assign each item to a bin without exceeding the bin capacity.
from hermax.model import Model


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    m = Model()
    bins = m.int_vector("bins", n, 0, num_bins - 1)
    for b in range(num_bins):
        m &= (sum(weights[j] * (bins[j] == b) for j in range(n)) <= capacity)
    return m, {"bins": bins}
