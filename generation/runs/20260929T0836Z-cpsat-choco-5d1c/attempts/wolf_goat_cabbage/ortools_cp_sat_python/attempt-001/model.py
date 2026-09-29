# Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across
# a river in a boat that carries the farmer and at most one item. The wolf must
# never be left alone with the goat, nor the goat with the cabbage. The answer
# lists, for each stage, which shore (0 = start, 1 = destination) each item and
# the boat are on.
from ortools.sat.python import cp_model


def build(instance):
    stage = instance["stage"]  # number of stages, including the first and the last

    model = cp_model.CpModel()

    wolf_pos = [model.new_bool_var(f"wolf_{i}") for i in range(stage)]
    goat_pos = [model.new_bool_var(f"goat_{i}") for i in range(stage)]
    cabbage_pos = [model.new_bool_var(f"cabbage_{i}") for i in range(stage)]
    boat_pos = [model.new_bool_var(f"boat_{i}") for i in range(stage)]

    # everything starts on the first shore
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        model.add(pos[0] == 0)
    # ... and ends on the far shore
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        model.add(pos[stage - 1] == 1)

    # the boat crosses the river at every stage
    for i in range(1, stage):
        model.add(boat_pos[i] != boat_pos[i - 1])

    for i in range(stage):
        # the wolf and the goat are never alone together: if they share a shore the boat is there too
        wolf_with_goat = model.new_bool_var(f"wolf_with_goat_{i}")
        model.add(goat_pos[i] == wolf_pos[i]).only_enforce_if(wolf_with_goat)
        model.add(goat_pos[i] != wolf_pos[i]).only_enforce_if(wolf_with_goat.negated())
        model.add(boat_pos[i] == wolf_pos[i]).only_enforce_if(wolf_with_goat)
        # the goat and the cabbage are never alone together
        goat_with_cabbage = model.new_bool_var(f"goat_with_cabbage_{i}")
        model.add(goat_pos[i] == cabbage_pos[i]).only_enforce_if(goat_with_cabbage)
        model.add(goat_pos[i] != cabbage_pos[i]).only_enforce_if(goat_with_cabbage.negated())
        model.add(boat_pos[i] == goat_pos[i]).only_enforce_if(goat_with_cabbage)

    # at most one of the wolf, goat and cabbage changes shore between two stages
    for i in range(stage - 1):
        moved = []
        for pos in (wolf_pos, goat_pos, cabbage_pos):
            changes = model.new_bool_var(f"changes_{i}")
            model.add(pos[i] != pos[i + 1]).only_enforce_if(changes)
            model.add(pos[i] == pos[i + 1]).only_enforce_if(changes.negated())
            moved.append(changes)
        model.add(sum(moved) <= 1)

    return model, {"wolf_pos": wolf_pos, "goat_pos": goat_pos, "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}
