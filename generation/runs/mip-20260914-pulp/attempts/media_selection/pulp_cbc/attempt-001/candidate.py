import pulp


def build(instance):
    incidence, costs = instance["incidence_matrix"], instance["media_costs"]
    audiences, media = range(len(instance["target_audiences"])), range(len(instance["advertising_media"]))
    problem = pulp.LpProblem("media_selection", pulp.LpMinimize)
    selected = [pulp.LpVariable(f"media_{m}", cat="Binary") for m in media]
    for t in audiences:
        problem += pulp.lpSum(incidence[t][m] * selected[m] for m in media) >= 1
    total = pulp.lpSum(costs[m] * selected[m] for m in media)
    problem += total
    return problem, {"is_selected": selected, "min_total_cost": total}
