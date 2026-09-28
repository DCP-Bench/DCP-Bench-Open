"""Four numbers: find three integers in 1..10 from whose subset sums every given number can be made."""
import gurobipy as gp
from gurobipy import GRB

# The three numbers to find each lie in 1..10, as the problem states.
LOW, HIGH = 1, 10
PARTS = range(3)


def build(instance):
    numbers = instance["numbers"]
    targets = range(len(numbers))

    model = gp.Model("four_numbers")

    # x[j] is the j-th of the three numbers.
    x = model.addVars(PARTS, lb=LOW, ub=HIGH, vtype=GRB.INTEGER, name="x")

    # uses[i, j] is 1 when x[j] is part of the subset that sums to numbers[i].
    uses = model.addVars(targets, PARTS, vtype=GRB.BINARY, name="uses")

    # part[i, j] is uses[i, j] * x[j]. A product of two variables would drop the
    # licence's variable limit to 200, so it is written linearly: part is 0 when
    # uses is 0, and equals x[j] when uses is 1, using the bounds 1..10 of x.
    part = model.addVars(targets, PARTS, lb=0, ub=HIGH, vtype=GRB.INTEGER, name="part")
    for i in targets:
        for j in PARTS:
            model.addConstr(part[i, j] <= HIGH * uses[i, j], name=f"off_high[{i},{j}]")
            model.addConstr(part[i, j] >= LOW * uses[i, j], name=f"off_low[{i},{j}]")
            model.addConstr(part[i, j] <= x[j] - LOW * (1 - uses[i, j]), name=f"on_high[{i},{j}]")
            model.addConstr(part[i, j] >= x[j] - HIGH * (1 - uses[i, j]), name=f"on_low[{i},{j}]")

    # Each given number is the sum of its subset of the three.
    for i in targets:
        model.addConstr(part.sum(i, "*") == numbers[i], name=f"sum[{i}]")

    return model, {"x": [x[j] for j in PARTS]}
