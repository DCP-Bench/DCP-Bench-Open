# Cheapest set of media that still reaches every audience.
from dcp_pb import Pb


def build(instance):
    incidence = instance["incidence_matrix"]
    costs = instance["media_costs"]
    audiences = len(instance["target_audiences"])
    media = len(instance["advertising_media"])

    pb = Pb()
    selected = pb.bools(media)
    for target in range(audiences):
        pb.ge([(incidence[target][m], selected[m]) for m in range(media)], 1)

    spend = pb.int(0, sum(costs))
    pb.eq(list(zip(costs, selected)) + [(-1, spend)], 0)
    pb.minimise([(1, spend)])
    return pb, {"is_selected": selected, "min_total_cost": spend}
