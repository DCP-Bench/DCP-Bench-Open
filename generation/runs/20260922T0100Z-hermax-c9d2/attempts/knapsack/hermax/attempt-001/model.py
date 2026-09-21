# Maximise the value carried without exceeding the knapsack capacity.
from dcp_maxsat import MaxSat


def reachable(weights):
    """Every total a subset of these weights can add up to."""
    totals = {0}
    for weight in weights:
        totals |= {total + weight for total in totals}
    return sorted(totals)


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]

    sat = MaxSat()
    x = sat.bools(len(values))
    sat.bool_sum_le(weights, x, capacity)
    profit = sat.int_from(reachable(values))
    sat.link_bool_sum(values, x, profit)
    return sat, {"x": x}, ("maximize", profit)
