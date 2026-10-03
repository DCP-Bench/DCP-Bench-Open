# Media selection: choose which advertising media to buy so that every target audience is
# reached by at least one chosen medium, at the lowest total cost.
from pychoco.model import Model


def build(instance):
    incidence = instance["incidence_matrix"]  # incidence[t][m] = 1 if audience t is reached by medium m
    media_costs = instance["media_costs"]  # media_costs[m] = cost of medium m
    num_audiences = len(instance["target_audiences"])
    num_media = len(instance["advertising_media"])

    model = Model()

    # is_selected[m] = 1 if medium m is bought
    is_selected = [model.boolvar(name=f"is_selected_{m}") for m in range(num_media)]

    # each audience is covered by at least one chosen medium
    for t in range(num_audiences):
        model.scalar(is_selected, [incidence[t][m] for m in range(num_media)], ">=", 1).post()

    # total cost of the chosen media, the quantity to minimise
    min_total_cost = model.intvar(0, sum(media_costs), name="min_total_cost")
    model.scalar(is_selected, media_costs, "=", min_total_cost).post()

    return model, {"is_selected": is_selected, "min_total_cost": min_total_cost}, ("minimize", min_total_cost)
