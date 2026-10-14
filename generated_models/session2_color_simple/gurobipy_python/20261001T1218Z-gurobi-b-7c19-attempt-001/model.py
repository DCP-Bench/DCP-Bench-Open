"""Map colouring: colour six countries so that neighbours differ, using as few colours as possible."""
import gurobipy as gp
from gurobipy import GRB

# The six countries (Belgium, Denmark, France, Germany, Netherlands,
# Luxembourg) belong to the problem; the reference fixes their number at 6.
NUM_NODES = 6


def build(instance):
    graph = instance["graph"]
    nodes = range(NUM_NODES)
    colours = range(1, NUM_NODES + 1)

    model = gp.Model("session2_color_simple")

    # paint[i, c] = 1 when country i has colour c; colors[i] reads it back.
    paint = model.addVars(nodes, colours, vtype=GRB.BINARY, name="paint")
    for i in nodes:
        model.addConstr(paint.sum(i, "*") == 1, name=f"one_colour[{i}]")
    colors = [gp.quicksum(c * paint[i, c] for c in colours) for i in nodes]

    # Two neighbouring countries cannot have the same colour (countries are
    # numbered from 1 in the instance).
    for k, (i, j) in enumerate(graph):
        for c in colours:
            model.addConstr(paint[i - 1, c] + paint[j - 1, c] <= 1, name=f"neighbours[{k},{c}]")

    # Minimise the number of colours used, the largest colour of any country.
    used = model.addVar(lb=1, ub=NUM_NODES, vtype=GRB.INTEGER, name="used")
    for i in nodes:
        model.addConstr(used >= colors[i], name=f"used_covers[{i}]")
    model.setObjective(used, GRB.MINIMIZE)

    return model, {"colors": colors}
