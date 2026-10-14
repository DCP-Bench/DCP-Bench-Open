# Wolf, goat and cabbage: a farmer must ferry a wolf, a goat and a cabbage across a river
# in a boat that carries only the farmer and one item. The wolf eats the goat and the goat
# eats the cabbage if left alone together. Give the shore (0 = start, 1 = destination) of
# each of them and of the boat at every stage, from everyone on the start shore to
# everyone on the destination shore.
from pychoco.model import Model


def build(instance):
    stage = instance["stage"]  # number of stages

    model = Model()

    # position of each at every stage: false = starting shore, true = destination shore
    wolf_pos = [model.boolvar(name=f"wolf_{i}") for i in range(stage)]
    goat_pos = [model.boolvar(name=f"goat_{i}") for i in range(stage)]
    cabbage_pos = [model.boolvar(name=f"cabbage_{i}") for i in range(stage)]
    boat_pos = [model.boolvar(name=f"boat_{i}") for i in range(stage)]

    # initial situation: everyone on the starting shore
    for pos in (boat_pos, wolf_pos, goat_pos, cabbage_pos):
        model.arithm(pos[0], "=", 0).post()

    # final situation: everyone on the destination shore
    for pos in (boat_pos, wolf_pos, goat_pos, cabbage_pos):
        model.arithm(pos[stage - 1], "=", 1).post()

    # the boat keeps moving between the shores
    for i in range(1, stage):
        model.arithm(boat_pos[i], "!=", boat_pos[i - 1]).post()

    for i in range(stage):
        # the wolf and the goat cannot be left alone: if they share a shore, so does the boat
        model.or_([model.arithm(goat_pos[i], "!=", wolf_pos[i]),
                   model.arithm(boat_pos[i], "=", wolf_pos[i])]).post()
        # the goat and the cabbage cannot be left alone: if they share a shore, so does the boat
        model.or_([model.arithm(goat_pos[i], "!=", cabbage_pos[i]),
                   model.arithm(boat_pos[i], "=", goat_pos[i])]).post()

    # only one of the wolf, goat and cabbage can move per turn
    for i in range(stage - 1):
        moved = [model.arithm(pos[i], "!=", pos[i + 1]).reify() for pos in (wolf_pos, goat_pos, cabbage_pos)]
        model.sum(moved, "<=", 1).post()

    return model, {"wolf_pos": wolf_pos, "goat_pos": goat_pos,
                   "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}
