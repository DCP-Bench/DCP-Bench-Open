import cpmpy as cp


def build(instance):
    incidence, costs = instance["incidence_matrix"], instance["media_costs"]
    audiences, media = len(instance["target_audiences"]), len(instance["advertising_media"])
    selected = cp.boolvar(shape=media, name="is_selected")
    model = cp.Model()
    for t in range(audiences):
        model += cp.sum([incidence[t][m] * selected[m] for m in range(media)]) >= 1
    total = cp.sum([costs[m] * selected[m] for m in range(media)])
    model.minimize(total)
    return model, {"is_selected": [selected[m] for m in range(media)], "min_total_cost": total}
