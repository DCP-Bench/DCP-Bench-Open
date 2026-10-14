# Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across
# a river in a boat that carries the farmer and at most one item. The wolf must
# never be left alone with the goat, nor the goat with the cabbage. The answer
# lists, for each stage, which shore (false = start, true = destination) each
# item and the boat are on.
from pysat.formula import CNF, IDPool


def build(instance):
    stage = instance["stage"]  # number of stages, including the first and the last

    pool = IDPool()
    wolf_pos = [pool.id(("wolf", i)) for i in range(stage)]
    goat_pos = [pool.id(("goat", i)) for i in range(stage)]
    cabbage_pos = [pool.id(("cabbage", i)) for i in range(stage)]
    boat_pos = [pool.id(("boat", i)) for i in range(stage)]

    cnf = CNF()
    # everything starts on the first shore ...
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        cnf.append([-pos[0]])
    # ... and ends on the far shore
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        cnf.append([pos[stage - 1]])

    # the boat crosses the river at every stage: its shore differs from the previous stage
    for i in range(1, stage):
        cnf.append([boat_pos[i], boat_pos[i - 1]])
        cnf.append([-boat_pos[i], -boat_pos[i - 1]])

    for i in range(stage):
        # the wolf and the goat are never alone together: if they share a shore the
        # boat is there too (no stage with both on one shore and the boat on the other)
        cnf.append([-goat_pos[i], -wolf_pos[i], boat_pos[i]])
        cnf.append([goat_pos[i], wolf_pos[i], -boat_pos[i]])
        # the goat and the cabbage are never alone together
        cnf.append([-goat_pos[i], -cabbage_pos[i], boat_pos[i]])
        cnf.append([goat_pos[i], cabbage_pos[i], -boat_pos[i]])

    # at most one of the wolf, goat and cabbage changes shore between two stages
    for i in range(stage - 1):
        moved = []
        for who, pos in (("wolf", wolf_pos), ("goat", goat_pos), ("cabbage", cabbage_pos)):
            change = pool.id(("moved", who, i))
            # change <-> the item is on different shores at stages i and i + 1
            cnf.append([-change, pos[i], pos[i + 1]])
            cnf.append([-change, -pos[i], -pos[i + 1]])
            cnf.append([change, -pos[i], pos[i + 1]])
            cnf.append([change, pos[i], -pos[i + 1]])
            moved.append(change)
        for a in range(3):
            for b in range(a + 1, 3):
                cnf.append([-moved[a], -moved[b]])

    return cnf, {"wolf_pos": wolf_pos, "goat_pos": goat_pos, "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}
