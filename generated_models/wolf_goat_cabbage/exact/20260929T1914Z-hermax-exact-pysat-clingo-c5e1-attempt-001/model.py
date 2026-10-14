# Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across
# a river in a boat that carries the farmer and at most one item. The wolf must
# never be left alone with the goat, nor the goat with the cabbage. The answer
# lists, for each stage, which shore (0 = start, 1 = destination) each item and
# the boat are on.
from exact import Exact


def build(instance):
    stage = instance["stage"]  # number of stages, including the first and the last

    solver = Exact()
    names = {}
    for who in ("wolf", "goat", "cabbage", "boat"):
        names[who] = [f"{who}_{i}" for i in range(stage)]
        for name in names[who]:
            solver.addVariable(name, 0, 1)
    wolf, goat, cabbage, boat = names["wolf"], names["goat"], names["cabbage"], names["boat"]

    # everything starts on the first shore ... and ends on the far shore
    for who in names.values():
        solver.addConstraint([(1, who[0])], True, 0, True, 0)
        solver.addConstraint([(1, who[stage - 1])], True, 1, True, 1)

    # the boat crosses the river at every stage: its shore differs from the previous stage
    for i in range(1, stage):
        solver.addConstraint([(1, boat[i]), (1, boat[i - 1])], True, 1, True, 1)

    for i in range(stage):
        # the wolf and the goat are never alone together: if they share a shore the
        # boat is there too. Both on shore 1 needs the boat on 1; both on 0 needs it on 0.
        solver.addConstraint([(1, boat[i]), (-1, goat[i]), (-1, wolf[i])], True, -1)
        solver.addConstraint([(1, goat[i]), (1, wolf[i]), (-1, boat[i])], True, 0)
        # the goat and the cabbage are never alone together
        solver.addConstraint([(1, boat[i]), (-1, goat[i]), (-1, cabbage[i])], True, -1)
        solver.addConstraint([(1, goat[i]), (1, cabbage[i]), (-1, boat[i])], True, 0)

    # at most one of the wolf, goat and cabbage changes shore between two stages
    for i in range(stage - 1):
        moved = []
        for who in (wolf, goat, cabbage):
            change = f"moved_{who[0].split('_')[0]}_{i}"
            solver.addVariable(change, 0, 1)
            a, b = who[i], who[i + 1]
            # change = |a - b|, written as four linear bounds
            solver.addConstraint([(1, change), (-1, a), (1, b)], True, 0)
            solver.addConstraint([(1, change), (1, a), (-1, b)], True, 0)
            solver.addConstraint([(1, change), (-1, a), (-1, b)], False, 0, True, 0)
            solver.addConstraint([(1, change), (1, a), (1, b)], False, 0, True, 2)
            moved.append((1, change))
        solver.addConstraint(moved, False, 0, True, 1)

    return solver, {"wolf_pos": wolf, "goat_pos": goat, "cabbage_pos": cabbage, "boat_pos": boat}
