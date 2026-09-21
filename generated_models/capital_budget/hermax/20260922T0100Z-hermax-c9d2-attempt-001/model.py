# Choose investments to maximise net present value within the budget.
from dcp_maxsat import MaxSat


def reachable(weights):
    """Every total a subset of these weights can add up to."""
    totals = {0}
    for weight in weights:
        totals |= {total + weight for total in totals}
    return sorted(totals)


def build(instance):
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    budget = instance["budget"]

    sat = MaxSat()
    x = sat.bools(len(npv))
    sat.bool_sum_le(cash_flow, x, budget)
    z = sat.int_from(reachable(npv))
    sat.link_bool_sum(npv, x, z)
    return sat, {"x": x, "z": z}, ("maximize", z)
