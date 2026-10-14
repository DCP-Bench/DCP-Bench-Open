"""Media selection: pick advertising media so that every target audience is reached at the least cost."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    reaches = instance["incidence_matrix"]  # reaches[t][m] is 1 if medium m reaches audience t
    media_costs = instance["media_costs"]
    audiences = range(len(instance["target_audiences"]))
    media = range(len(instance["advertising_media"]))

    model = gp.Model("media_selection")

    # is_selected[m] is 1 when medium m is part of the campaign.
    is_selected = model.addVars(media, vtype=GRB.BINARY, name="is_selected")

    # Every target audience is reached by at least one selected medium.
    for t in audiences:
        model.addConstr(gp.quicksum(reaches[t][m] * is_selected[m] for m in media) >= 1,
                        name=f"audience[{t}]")

    # Minimise the cost of the campaign.
    min_total_cost = gp.quicksum(media_costs[m] * is_selected[m] for m in media)
    model.setObjective(min_total_cost, GRB.MINIMIZE)

    return model, {"is_selected": [is_selected[m] for m in media], "min_total_cost": min_total_cost}
