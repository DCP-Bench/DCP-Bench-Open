import z3


def build(instance):
    incidence, costs = instance["incidence_matrix"], instance["media_costs"]
    audiences, media = len(instance["target_audiences"]), len(instance["advertising_media"])
    selected = [z3.Bool(f"m_{m}") for m in range(media)]
    picked = [z3.If(selected[m], 1, 0) for m in range(media)]
    constraints = [z3.Sum([incidence[t][m] * picked[m] for m in range(media)]) >= 1
                   for t in range(audiences)]
    total = z3.Sum([costs[m] * picked[m] for m in range(media)])
    return constraints, {"is_selected": selected, "min_total_cost": total}, ("minimize", total)
