# Cheapest set of media that still reaches every audience.
from exact import Exact


def build(instance):
    incidence = instance["incidence_matrix"]
    costs = instance["media_costs"]
    audiences = len(instance["target_audiences"])
    media = len(instance["advertising_media"])

    solver = Exact()
    selected = [f"s{k}" for k in range(media)]
    for name in selected:
        solver.addVariable(name, 0, 1)
    for target in range(audiences):
        solver.addConstraint(
            [(incidence[target][k], selected[k]) for k in range(media)
             if incidence[target][k]], True, 1)

    solver.addVariable("spend", 0, sum(costs))
    solver.addConstraint(list(zip(costs, selected)) + [(-1, "spend")],
                         True, 0, True, 0)
    return (solver, {"is_selected": selected, "min_total_cost": "spend"},
            ("minimize", [(1, "spend")]))
