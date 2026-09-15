from ortools.sat.python import cp_model


def build(instance):
    """Wolf, goat and cabbage: cross the river without anything being eaten.

    A 1 means that item is on the destination shore at that stage.
    """
    stage = instance["stage"]

    model = cp_model.CpModel()
    wolf_pos = [model.new_bool_var(f"wolf{i}") for i in range(stage)]
    goat_pos = [model.new_bool_var(f"goat{i}") for i in range(stage)]
    cabbage_pos = [model.new_bool_var(f"cabbage{i}") for i in range(stage)]
    boat_pos = [model.new_bool_var(f"boat{i}") for i in range(stage)]

    # Everything starts on the near shore and ends on the far one.
    for row in (boat_pos, wolf_pos, goat_pos, cabbage_pos):
        model.add(row[0] == 0)
        model.add(row[-1] == 1)

    # The boat crosses on every stage.
    for i in range(1, stage):
        model.add(boat_pos[i] != boat_pos[i - 1])

    def same(first, second, name):
        """A Boolean that is true exactly when the two agree."""
        agrees = model.new_bool_var(name)
        model.add(first == second).only_enforce_if(agrees)
        model.add(first != second).only_enforce_if(~agrees)
        return agrees

    for i in range(stage):
        # The wolf and the goat are never left alone together.
        model.add_bool_or([
            ~same(goat_pos[i], wolf_pos[i], f"gw{i}"),
            same(boat_pos[i], wolf_pos[i], f"bw{i}"),
        ])
        # Nor the goat and the cabbage.
        model.add_bool_or([
            ~same(goat_pos[i], cabbage_pos[i], f"gc{i}"),
            same(boat_pos[i], goat_pos[i], f"bg{i}"),
        ])

    # The boat carries at most one passenger per crossing.
    for i in range(stage - 1):
        moves = []
        for row, label in (
            (wolf_pos, "w"), (goat_pos, "g"), (cabbage_pos, "c")
        ):
            moved = model.new_int_var(0, 1, f"moved_{label}{i}")
            model.add_abs_equality(moved, row[i] - row[i + 1])
            moves.append(moved)
        model.add(sum(moves) <= 1)

    return model, {
        "wolf_pos": wolf_pos, "goat_pos": goat_pos,
        "cabbage_pos": cabbage_pos, "boat_pos": boat_pos,
    }
