# Media selection: choose which advertising media to buy so that every target audience
# is reached, at minimum total campaign cost.
# incidence_matrix[i][j] = 1 when medium j reaches audience i; media_costs[j] is the cost of medium j.
import mip


def build(instance):
    costs = instance["media_costs"]
    incidence = instance["incidence_matrix"]
    n_media = len(instance["advertising_media"])
    n_audiences = len(instance["target_audiences"])

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.verbose = 0
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    # one binary per medium: 1 when the medium is selected
    is_selected = [model.add_var(f"is_selected_{j}", var_type=mip.BINARY) for j in range(n_media)]

    # the total cost of the selected media
    total = model.add_var("min_total_cost", var_type=mip.INTEGER, lb=0, ub=sum(costs))
    model.add_constr(total == mip.xsum(costs[j] * is_selected[j] for j in range(n_media)))

    # all audiences are reached: each audience is covered by at least one selected medium
    # (covering more than once is allowed)
    for i in range(n_audiences):
        model.add_constr(mip.xsum(incidence[i][j] * is_selected[j] for j in range(n_media)) >= 1)

    # the campaign does not spend more than necessary: minimise the total cost
    model.objective = total

    return model, {"is_selected": is_selected, "min_total_cost": total}
