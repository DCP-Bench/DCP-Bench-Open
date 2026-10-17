import mip


def build(instance):
    n = instance["n"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = model.add_var("x", lb=0, ub=n, var_type=mip.INTEGER)
    y = model.add_var("y", lb=0, ub=n, var_type=mip.INTEGER)
    if instance["optimize"]:
        model += x + y >= n
        model.objective = x + y
    else:
        model += x + y == n
    return model, {"x": x, "y": y}
