"""Wolf, goat and cabbage: a farmer with a wolf, a goat and a cabbage crosses a river by boat.
The boat carries the farmer and at most one of the others. Left alone together, the wolf eats
the goat and the goat eats the cabbage. Find a sequence of stages that brings everything to the
other shore without anything being eaten.

The model reports, for every stage, on which shore the wolf, the goat, the cabbage and the boat
are: 0 for the starting shore, 1 for the destination shore.
"""
import pulp


def build(instance):
    stage = instance["stage"]  # number of stages, the first and the last included

    problem = pulp.LpProblem("wolf_goat_cabbage", pulp.LpMinimize)  # satisfaction: no objective

    # the shore (0 start, 1 destination) of each of them at each stage
    wolf_pos = [pulp.LpVariable(f"wolf_{i}", cat="Binary") for i in range(stage)]
    goat_pos = [pulp.LpVariable(f"goat_{i}", cat="Binary") for i in range(stage)]
    cabbage_pos = [pulp.LpVariable(f"cabbage_{i}", cat="Binary") for i in range(stage)]
    boat_pos = [pulp.LpVariable(f"boat_{i}", cat="Binary") for i in range(stage)]

    # at the first stage everything is on the starting shore
    for pos in (boat_pos, wolf_pos, goat_pos, cabbage_pos):
        problem += pos[0] == 0

    # at the last stage everything is on the destination shore
    for pos in (boat_pos, wolf_pos, goat_pos, cabbage_pos):
        problem += pos[stage - 1] == 1

    # the boat crosses at every stage: it is on the other shore than at the stage before
    for i in range(1, stage):
        problem += boat_pos[i] + boat_pos[i - 1] == 1

    for i in range(stage):
        # The wolf and the goat are not left alone: if they are on the same shore, the boat
        # (with the farmer) is there too. The wolf and the goat are together without the boat
        # when wolf + goat - boat is -1 (both on the start shore, the boat on the destination
        # shore) or 2 (both on the destination shore, the boat on the start shore).
        problem += wolf_pos[i] + goat_pos[i] - boat_pos[i] >= 0
        problem += wolf_pos[i] + goat_pos[i] - boat_pos[i] <= 1

        # the goat and the cabbage are not left alone, in the same way
        problem += goat_pos[i] + cabbage_pos[i] - boat_pos[i] >= 0
        problem += goat_pos[i] + cabbage_pos[i] - boat_pos[i] <= 1

    # At most one of the wolf, the goat and the cabbage changes shore from one stage to the
    # next (the boat carries one of them). moved[i][k] is at least the change of the k-th of
    # them between stage i and i + 1, whichever direction; the changes add up to at most 1.
    for i in range(stage - 1):
        moved = []
        for k, pos in enumerate((wolf_pos, goat_pos, cabbage_pos)):
            change = pulp.LpVariable(f"moved_{i}_{k}", 0, 1)
            problem += change >= pos[i] - pos[i + 1]
            problem += change >= pos[i + 1] - pos[i]
            moved.append(change)
        problem += pulp.lpSum(moved) <= 1

    return problem, {"wolf_pos": wolf_pos, "goat_pos": goat_pos,
                     "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}
