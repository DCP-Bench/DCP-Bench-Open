# Maximise the value carried without exceeding the knapsack capacity.
from dcp_pb import Pb


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]

    pb = Pb()
    x = pb.bools(len(values))
    pb.weighted_sum_le(weights, x, capacity)
    pb.maximise(list(zip(values, x)))
    return pb, {"x": x}
