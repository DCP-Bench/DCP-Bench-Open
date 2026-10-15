from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    model = Model()
    x = model.addVar(name="x", vtype="I", lb=0, ub=n)
    y = model.addVar(name="y", vtype="I", lb=0, ub=n)
    if instance["optimize"]:
        model.addCons(x + y >= n)
        model.setObjective(x + y, "minimize")
    else:
        model.addCons(x + y == n)
    return model, {"x": x, "y": y}
