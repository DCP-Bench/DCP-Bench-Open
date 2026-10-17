import mip


def build(instance):
    n = instance["n"]
    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    x = m.add_var("x", lb=0, ub=n, var_type=mip.INTEGER)
    y = m.add_var("y", lb=0, ub=n, var_type=mip.INTEGER)
    if instance["optimize"]:
        m += x + y >= n
        m.objective = x + y
    else:
        m += x + y == n
    return m, {"x": x, "y": y}
