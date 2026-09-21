# Assign each item to a bin without exceeding the bin capacity.
from dcp_maxsat import MaxSat


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    sat = MaxSat()
    bins = sat.ints(n, 0, num_bins - 1)
    for b in range(num_bins):
        here = [bins[j].literal(b) for j in range(n)]
        sat.bool_sum_le(weights, here, capacity)
    return sat, {"bins": bins}
