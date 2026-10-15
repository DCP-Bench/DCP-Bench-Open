# Media selection: choose advertising media so every target audience is reached, at minimum total cost.
from pyscipopt import Model, quicksum


def build(instance):
    media = instance["advertising_media"]
    audiences = instance["target_audiences"]
    cover = instance["incidence_matrix"]  # cover[a][m] = 1 if medium m reaches audience a
    cost = instance["media_costs"]

    m = Model()

    # selected[k] = 1 if medium media[k] is bought
    selected = [m.addVar(name=f"selected_{k}", vtype="B") for k in range(len(media))]

    # every audience is reached by at least one selected medium
    # (an audience reached more than once is fine)
    for a in range(len(audiences)):
        reaching = [selected[k] for k in range(len(media)) if cover[a][k] == 1]
        m.addCons(quicksum(reaching) >= 1)

    # total campaign cost, to be minimised
    total_cost = quicksum(cost[k] * selected[k] for k in range(len(media)))
    m.setObjective(total_cost, "minimize")

    # outputs: the selection flags, and the minimum total cost
    return m, {"is_selected": selected, "min_total_cost": total_cost}
