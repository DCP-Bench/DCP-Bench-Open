# Assign each item to a bin without exceeding the bin capacity.
from dcp_pb import Pb


def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    pb = Pb()
    bins = pb.ints(n, 0, num_bins - 1)
    for b in range(num_bins):
        here = [pb.is_value(bins[j], b) for j in range(n)]
        pb.le(list(zip(weights, here)), capacity)
    return pb, {"bins": bins}
