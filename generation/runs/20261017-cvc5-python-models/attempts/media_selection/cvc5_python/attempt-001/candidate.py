# Media selection: choose which advertising media to buy so that every target
# audience is reached by at least one selected medium, at minimum total campaign cost.
# Rows of incidence_matrix are audiences, columns are media (1 = the medium reaches
# the audience). Outputs: is_selected (one Boolean per medium) and min_total_cost.

import cvc5.pythonic as cz


def build(instance):
    incidence = instance["incidence_matrix"]
    costs = instance["media_costs"]
    n_audiences = len(instance["target_audiences"])
    n_media = len(instance["advertising_media"])

    selected = [cz.Bool(f"is_selected_{j}") for j in range(n_media)]
    total = cz.Int("min_total_cost")

    constraints = []

    # Every target audience is covered by at least one selected medium.
    # Each audience's covering media are the columns where its incidence row is 1.
    for i in range(n_audiences):
        covering = [selected[j] for j in range(n_media) if incidence[i][j] == 1]
        if not covering:
            constraints.append(cz.BoolVal(False))
        elif len(covering) == 1:
            constraints.append(covering[0])
        else:
            constraints.append(cz.Or(covering))

    # The total campaign cost is the sum of the costs of the selected media.
    # Sum over Booleans is not allowed, so each media contributes If(selected, cost, 0).
    cost_terms = [cz.If(selected[j], costs[j], 0) for j in range(n_media)]
    constraints.append(total == cz.Sum(cost_terms))

    outputs = {
        "is_selected": selected,
        "min_total_cost": total,
    }
    return constraints, outputs, ("minimize", total)
