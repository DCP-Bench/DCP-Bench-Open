from docplex.mp.model import Model


def build(instance):
    n = instance["n"]
    model = Model()
    x = model.integer_var(0, n, name="x")
    y = model.integer_var(0, n, name="y")
    if instance["optimize"]:
        model.add_constraint(x + y >= n)
        model.minimize(x + y)
    else:
        model.add_constraint(x + y == n)
    return model, {"x": x, "y": y}
