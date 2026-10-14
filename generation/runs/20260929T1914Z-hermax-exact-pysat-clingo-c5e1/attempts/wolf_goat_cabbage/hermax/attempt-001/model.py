# Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across
# a river in a boat that carries the farmer and at most one item. The wolf must
# never be left alone with the goat, nor the goat with the cabbage. The answer
# lists, for each stage, which shore (false = start, true = destination) each
# item and the boat are on.
from hermax.model import Model


def build(instance):
    stage = instance["stage"]  # number of stages, including the first and the last

    m = Model()
    wolf_pos = m.bool_vector("wolf_pos", stage)
    goat_pos = m.bool_vector("goat_pos", stage)
    cabbage_pos = m.bool_vector("cabbage_pos", stage)
    boat_pos = m.bool_vector("boat_pos", stage)

    # everything starts on the first shore ...
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        m &= ~pos[0]
    # ... and ends on the far shore
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        m &= pos[stage - 1]

    # the boat crosses the river at every stage: its shore differs from the previous stage
    for i in range(1, stage):
        m &= (boat_pos[i] | boat_pos[i - 1])
        m &= (~boat_pos[i] | ~boat_pos[i - 1])

    for i in range(stage):
        # the wolf and the goat are never alone together: if they share a shore the
        # boat is there too (no stage with both on one shore and the boat on the other)
        m &= (~goat_pos[i] | ~wolf_pos[i] | boat_pos[i])
        m &= (goat_pos[i] | wolf_pos[i] | ~boat_pos[i])
        # the goat and the cabbage are never alone together
        m &= (~goat_pos[i] | ~cabbage_pos[i] | boat_pos[i])
        m &= (goat_pos[i] | cabbage_pos[i] | ~boat_pos[i])

    # at most one of the wolf, goat and cabbage changes shore between two stages
    for i in range(stage - 1):
        changes = []
        for pos in (wolf_pos, goat_pos, cabbage_pos):
            moved = m.bool(f"moved_{len(changes)}_{i}")
            # moved <-> the item is on different shores at stages i and i + 1
            m &= (~moved | pos[i] | pos[i + 1])
            m &= (~moved | ~pos[i] | ~pos[i + 1])
            m &= (moved | ~pos[i] | pos[i + 1])
            m &= (moved | pos[i] | ~pos[i + 1])
            changes.append(moved)
        m &= (~changes[0] | ~changes[1])
        m &= (~changes[0] | ~changes[2])
        m &= (~changes[1] | ~changes[2])

    return m, {"wolf_pos": wolf_pos, "goat_pos": goat_pos, "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}
