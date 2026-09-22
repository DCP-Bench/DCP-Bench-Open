# Cheapest set of media that still reaches every audience.
from hermax.model import Model


def build(instance):
    incidence = instance["incidence_matrix"]
    costs = instance["media_costs"]
    audiences = len(instance["target_audiences"])
    media = len(instance["advertising_media"])

    m = Model()
    selected = m.bool_vector("is_selected", media)
    for target in range(audiences):
        m &= (sum(incidence[target][k] * selected[k] for k in range(media)) >= 1)

    # Minimising: buying a medium breaks its soft clause and pays its cost.
    for k in range(media):
        m.obj[costs[k]] += ~selected[k]

    spend = m.int("min_total_cost", 0, sum(costs))
    m &= (sum(costs[k] * selected[k] for k in range(media)) == spend)
    return m, {"is_selected": selected, "min_total_cost": spend}
