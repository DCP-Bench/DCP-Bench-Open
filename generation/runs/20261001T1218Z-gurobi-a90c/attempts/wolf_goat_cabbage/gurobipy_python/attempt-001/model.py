"""Wolf, goat and cabbage: ferry all three across the river, one at a time with the farmer, without anything being eaten."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    stage = instance["stage"]
    stages = range(stage)

    model = gp.Model("wolf_goat_cabbage")

    # 1 when the item is on the destination shore at a stage, 0 on the starting shore.
    wolf = model.addVars(stages, vtype=GRB.BINARY, name="wolf")
    goat = model.addVars(stages, vtype=GRB.BINARY, name="goat")
    cabbage = model.addVars(stages, vtype=GRB.BINARY, name="cabbage")
    boat = model.addVars(stages, vtype=GRB.BINARY, name="boat")

    # Initial situation: everything on the starting shore.
    for v in (boat, wolf, goat, cabbage):
        model.addConstr(v[0] == 0)

    # Final situation: everything on the destination shore.
    for v in (boat, wolf, goat, cabbage):
        model.addConstr(v[stage - 1] == 1)

    # The boat keeps moving between shores.
    for i in range(1, stage):
        model.addConstr(boat[i] + boat[i - 1] == 1, name=f"boat_moves[{i}]")

    for i in stages:
        # Wolf and goat cannot be left alone: if they share a shore, the boat is there.
        # Each line forbids one shore on which they would be left without the boat.
        model.addConstr(wolf[i] + goat[i] + (1 - boat[i]) >= 1, name=f"wolf_goat_start[{i}]")
        model.addConstr((1 - wolf[i]) + (1 - goat[i]) + boat[i] >= 1, name=f"wolf_goat_dest[{i}]")
        # Goat and cabbage cannot be left alone: if they share a shore, the boat is there.
        model.addConstr(goat[i] + cabbage[i] + (1 - boat[i]) >= 1, name=f"goat_cabbage_start[{i}]")
        model.addConstr((1 - goat[i]) + (1 - cabbage[i]) + boat[i] >= 1, name=f"goat_cabbage_dest[{i}]")

    # Only one of wolf, goat and cabbage can move per turn. moved[x, i] is at least
    # |x[i] - x[i+1]|, which for 0/1 values is 1 exactly when x changes shore.
    for i in range(stage - 1):
        moved = []
        for name, x in (("wolf", wolf), ("goat", goat), ("cabbage", cabbage)):
            m = model.addVar(vtype=GRB.BINARY, name=f"moved_{name}[{i}]")
            model.addConstr(m >= x[i] - x[i + 1])
            model.addConstr(m >= x[i + 1] - x[i])
            moved.append(m)
        model.addConstr(gp.quicksum(moved) <= 1, name=f"one_moves[{i}]")

    return model, {
        "wolf_pos": [wolf[i] for i in stages],
        "goat_pos": [goat[i] for i in stages],
        "cabbage_pos": [cabbage[i] for i in stages],
        "boat_pos": [boat[i] for i in stages],
    }
