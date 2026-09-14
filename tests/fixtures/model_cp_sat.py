from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    model = cp_model.CpModel()
    x, y = model.new_int_var(0, n, "x"), model.new_int_var(0, n, "y")
    model.add(x + y >= n if instance["optimize"] else x + y == n)
    if instance["optimize"]:
        model.minimize(x + y)
    return model, {"x": x, "y": y}
