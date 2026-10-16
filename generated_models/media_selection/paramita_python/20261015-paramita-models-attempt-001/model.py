# Media selection: choose advertising media so that every audience is reached at least once,
# at minimum total campaign cost.
from paramita.modelling import Bool


def build(instance):
    audiences = instance["target_audiences"]
    media = instance["advertising_media"]
    covers = instance["incidence_matrix"]  # covers[a][m] = 1 if medium m reaches audience a
    costs = instance["media_costs"]

    # is_selected[m] = 1 if medium m is bought
    select = [Bool(f"select_{m}") for m in range(len(media))]

    cons = []
    # every audience is reached by at least one selected medium (covering more than once is allowed)
    for a in range(len(audiences)):
        reaching = [select[m] for m in range(len(media)) if covers[a][m] == 1]
        cons.append(sum(reaching) >= 1)

    # total campaign cost: the cost of the selected media
    total_cost = sum(costs[m] * select[m] for m in range(len(media)))

    # the company wants the minimum campaign cost
    return cons, {"is_selected": select, "min_total_cost": total_cost}, ("minimize", total_cost)
