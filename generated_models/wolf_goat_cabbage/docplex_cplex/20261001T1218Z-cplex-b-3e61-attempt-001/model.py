"""Wolf, goat and cabbage: a farmer must ferry a wolf, a goat and a cabbage across a river in a boat
that carries at most one of them besides himself, never leaving the wolf alone with the goat or
the goat alone with the cabbage.

The model reports, at every stage, whether the wolf, goat, cabbage and boat are on the
destination shore (1) or the starting shore (0).
"""
from docplex.mp.model import Model


def build(instance):
    stage = instance["stage"]  # number of stages
    stages = range(stage)

    model = Model("wolf_goat_cabbage")

    wolf = [model.binary_var(name=f"wolf_{i}") for i in stages]
    goat = [model.binary_var(name=f"goat_{i}") for i in stages]
    cabbage = [model.binary_var(name=f"cabbage_{i}") for i in stages]
    boat = [model.binary_var(name=f"boat_{i}") for i in stages]

    # Initially everything is on the starting shore.
    for x in (boat, wolf, goat, cabbage):
        model.add_constraint(x[0] == 0)

    # The boat crosses the river at every stage.
    for i in range(1, stage):
        model.add_constraint(boat[i] + boat[i - 1] == 1)

    # Finally everything is on the destination shore.
    for x in (boat, wolf, goat, cabbage):
        model.add_constraint(x[-1] == 1)

    # The wolf and the goat cannot be left alone: they are never together on the shore the
    # boat is not on. On the starting shore (both 0, boat 1) and on the destination shore
    # (both 1, boat 0) this is one linear inequality each.
    for i in stages:
        model.add_constraint(boat[i] <= wolf[i] + goat[i])
        model.add_constraint(wolf[i] + goat[i] - boat[i] <= 1)

    # The goat and the cabbage cannot be left alone, in the same way.
    for i in stages:
        model.add_constraint(boat[i] <= goat[i] + cabbage[i])
        model.add_constraint(goat[i] + cabbage[i] - boat[i] <= 1)

    # Only one of the wolf, goat and cabbage can change shore per turn: the number of them
    # whose position changes is at most one. moved[x][i] is at least that change.
    for i in range(stage - 1):
        moved = []
        for name, x in (("wolf", wolf), ("goat", goat), ("cabbage", cabbage)):
            m = model.binary_var(name=f"moved_{name}_{i}")
            model.add_constraint(m >= x[i + 1] - x[i])
            model.add_constraint(m >= x[i] - x[i + 1])
            moved.append(m)
        model.add_constraint(model.sum(moved) <= 1)

    return model, {"wolf_pos": wolf, "goat_pos": goat, "cabbage_pos": cabbage, "boat_pos": boat}
