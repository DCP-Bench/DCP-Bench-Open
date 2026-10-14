# Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across
# a river in a boat that carries the farmer and at most one item. The wolf must
# never be left alone with the goat, nor the goat with the cabbage. The answer
# lists, for each stage, which shore (0 = start, 1 = destination) each item and
# the boat are on.
import z3


def build(instance):
    stage = instance["stage"]  # number of stages, including the first and the last

    solver = z3.Solver()

    wolf_pos = [z3.Bool(f"wolf_{i}") for i in range(stage)]
    goat_pos = [z3.Bool(f"goat_{i}") for i in range(stage)]
    cabbage_pos = [z3.Bool(f"cabbage_{i}") for i in range(stage)]
    boat_pos = [z3.Bool(f"boat_{i}") for i in range(stage)]

    # everything starts on the first shore
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        solver.add(z3.Not(pos[0]))
    # ... and ends on the far shore
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        solver.add(pos[stage - 1])

    # the boat crosses the river at every stage
    for i in range(1, stage):
        solver.add(boat_pos[i] != boat_pos[i - 1])

    for i in range(stage):
        # the wolf and the goat are never alone together: if they share a shore the boat is there too
        solver.add(z3.Or(goat_pos[i] != wolf_pos[i], boat_pos[i] == wolf_pos[i]))
        # the goat and the cabbage are never alone together
        solver.add(z3.Or(goat_pos[i] != cabbage_pos[i], boat_pos[i] == goat_pos[i]))

    # at most one of the wolf, goat and cabbage changes shore between two stages
    for i in range(stage - 1):
        solver.add(z3.AtMost(wolf_pos[i] != wolf_pos[i + 1], goat_pos[i] != goat_pos[i + 1],
                             cabbage_pos[i] != cabbage_pos[i + 1], 1))

    return solver, {"wolf_pos": wolf_pos, "goat_pos": goat_pos, "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}
