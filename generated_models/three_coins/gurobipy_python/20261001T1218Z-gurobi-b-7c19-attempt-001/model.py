"""Three coins: flip one coin per move so that after exactly num_moves moves all coins show the same face."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    num_moves = instance["num_moves"]
    init = instance["init"]
    n = len(init)

    model = gp.Model("three_coins")

    # steps[m][j] = 1 when coin j shows tails after move m (row 0 is the start).
    steps = [[model.addVar(vtype=GRB.BINARY, name=f"tails[{m},{j}]") for j in range(n)]
             for m in range(num_moves + 1)]

    # The coins start in the given configuration.
    for j in range(n):
        model.addConstr(steps[0][j] == init[j], name=f"start[{j}]")

    # Each move flips exactly one coin. flipped[m, j] = 1 when coin j differs
    # from the row before, the exclusive or of the two values.
    for m in range(1, num_moves + 1):
        flipped = []
        for j in range(n):
            f = model.addVar(vtype=GRB.BINARY, name=f"flipped[{m},{j}]")
            before, after = steps[m - 1][j], steps[m][j]
            model.addConstr(f >= before - after)
            model.addConstr(f >= after - before)
            model.addConstr(f <= before + after)
            model.addConstr(f <= 2 - before - after)
            flipped.append(f)
        model.addConstr(gp.quicksum(flipped) == 1, name=f"one_flip[{m}]")

    # At the end the coins are all heads or all tails.
    all_tails = model.addVar(vtype=GRB.BINARY, name="all_tails")
    model.addConstr(gp.quicksum(steps[num_moves]) == n * all_tails, name="all_same")

    return model, {"steps": steps}
