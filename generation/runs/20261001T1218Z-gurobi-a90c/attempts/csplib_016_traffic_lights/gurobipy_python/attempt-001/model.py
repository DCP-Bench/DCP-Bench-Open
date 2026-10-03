"""Traffic lights: set the eight lights of a four-way junction so that every pair of neighbouring roads shows an allowed combination."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    allowed = instance["allowed_tuples"]  # each row is (V_i, P_i, V_{i+1}, P_{i+1})
    tuples = range(len(allowed))

    model = gp.Model("traffic_lights")

    # Light states, a problem constant: a vehicle light is 0 red, 1 red-yellow,
    # 2 green, 3 yellow; a pedestrian light is 0 red, 1 green.
    vehicle = [model.addVar(lb=0, ub=3, vtype=GRB.INTEGER, name=f"V{i + 1}") for i in range(4)]
    pedestrian = [model.addVar(vtype=GRB.BINARY, name=f"P{i + 1}") for i in range(4)]

    # For each road i and the next one (road 4 is followed by road 1), the
    # combination (V_i, P_i, V_{i+1}, P_{i+1}) is one of the allowed tuples.
    # pick[i, k] is 1 when road i and its neighbour show the k-th allowed tuple.
    pick = model.addVars(4, tuples, vtype=GRB.BINARY, name="pick")
    for i in range(4):
        j = (i + 1) % 4
        corner = [vehicle[i], pedestrian[i], vehicle[j], pedestrian[j]]
        model.addConstr(pick.sum(i, "*") == 1, name=f"one_tuple[{i}]")
        for position in range(4):
            model.addConstr(
                corner[position] == gp.quicksum(allowed[k][position] * pick[i, k] for k in tuples),
                name=f"table[{i},{position}]",
            )

    return model, {"lights": vehicle + pedestrian}
