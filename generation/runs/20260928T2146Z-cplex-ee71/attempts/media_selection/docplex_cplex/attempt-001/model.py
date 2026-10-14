"""Media selection: pick advertising media so that every target audience is reached at the least cost."""
from docplex.mp.model import Model


def build(instance):
    reaches = instance["incidence_matrix"]  # reaches[t][m] is 1 if medium m reaches audience t
    media_costs = instance["media_costs"]
    audiences = range(len(instance["target_audiences"]))
    media = range(len(instance["advertising_media"]))

    model = Model("media_selection")

    # is_selected[m] is 1 when medium m is part of the campaign.
    is_selected = model.binary_var_list(len(media), name="is_selected")

    # Every target audience is reached by at least one selected medium.
    for t in audiences:
        model.add_constraint(model.sum(reaches[t][m] * is_selected[m] for m in media) >= 1,
                             ctname=f"audience_{t}")

    # Minimise the cost of the campaign.
    min_total_cost = model.dot(is_selected, media_costs)
    model.minimize(min_total_cost)

    return model, {"is_selected": is_selected, "min_total_cost": min_total_cost}
