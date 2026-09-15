from ortools.sat.python import cp_model


def build(instance):
    incidence, costs = instance["incidence_matrix"], instance["media_costs"]
    audiences, media = len(instance["target_audiences"]), len(instance["advertising_media"])
    model = cp_model.CpModel()
    selected = [model.new_bool_var(f"m_{m}") for m in range(media)]
    for t in range(audiences):
        model.add(sum(incidence[t][m] * selected[m] for m in range(media)) >= 1)
    total = sum(costs[m] * selected[m] for m in range(media))
    model.minimize(total)
    return model, {"is_selected": selected, "min_total_cost": total}
