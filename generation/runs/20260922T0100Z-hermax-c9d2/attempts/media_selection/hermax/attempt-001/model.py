# Cheapest set of media that still reaches every audience.
from dcp_maxsat import MaxSat


def reachable(weights):
    """Every total a subset of these weights can add up to."""
    totals = {0}
    for weight in weights:
        totals |= {total + weight for total in totals}
    return sorted(totals)


def build(instance):
    incidence = instance["incidence_matrix"]
    costs = instance["media_costs"]
    audiences = len(instance["target_audiences"])
    media = len(instance["advertising_media"])

    sat = MaxSat()
    selected = sat.bools(media)
    for target in range(audiences):
        covers = [incidence[target][m] for m in range(media)]
        sat.bool_sum_ge(covers, selected, 1)

    spend = sat.int_from(reachable(costs))
    sat.link_bool_sum(costs, selected, spend)
    return sat, {"is_selected": selected,
                 "min_total_cost": spend}, ("minimize", spend)
