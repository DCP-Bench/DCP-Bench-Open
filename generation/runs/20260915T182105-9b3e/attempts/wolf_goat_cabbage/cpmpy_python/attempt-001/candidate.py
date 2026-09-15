import cpmpy as cp


def build(instance):
    """Wolf, goat and cabbage: cross the river without anything being eaten.

    A 1 means that item is on the destination shore at that stage.
    """
    stage = instance["stage"]

    wolf_pos = cp.boolvar(stage, name="wolf_pos")
    goat_pos = cp.boolvar(stage, name="goat_pos")
    cabbage_pos = cp.boolvar(stage, name="cabbage_pos")
    boat_pos = cp.boolvar(stage, name="boat_pos")

    model = cp.Model(
        # Everything starts on the near shore.
        boat_pos[0] == 0,
        wolf_pos[0] == 0,
        goat_pos[0] == 0,
        cabbage_pos[0] == 0,
        # The boat crosses on every stage.
        [boat_pos[i] != boat_pos[i - 1] for i in range(1, stage)],
        # Everything ends on the far shore.
        boat_pos[-1] == 1,
        wolf_pos[-1] == 1,
        goat_pos[-1] == 1,
        cabbage_pos[-1] == 1,
        # The wolf and the goat are never left alone together.
        [
            (goat_pos[i] != wolf_pos[i]) | (boat_pos[i] == wolf_pos[i])
            for i in range(stage)
        ],
        # Nor the goat and the cabbage.
        [
            (goat_pos[i] != cabbage_pos[i]) | (boat_pos[i] == goat_pos[i])
            for i in range(stage)
        ],
        # The boat carries at most one passenger per crossing.
        [
            cp.abs(wolf_pos[i] - wolf_pos[i + 1])
            + cp.abs(goat_pos[i] - goat_pos[i + 1])
            + cp.abs(cabbage_pos[i] - cabbage_pos[i + 1])
            <= 1
            for i in range(stage - 1)
        ],
    )

    return model, {
        "wolf_pos": wolf_pos, "goat_pos": goat_pos,
        "cabbage_pos": cabbage_pos, "boat_pos": boat_pos,
    }
