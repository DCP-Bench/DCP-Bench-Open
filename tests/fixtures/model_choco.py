from pychoco.model import Model


def build(instance):
    n = instance["n"]
    model = Model()
    x = model.intvar(0, n, name="x")
    y = model.intvar(0, n, name="y")
    if not instance["optimize"]:
        model.arithm(x, "+", y, "=", n).post()
        return model, {"x": x, "y": y}
    model.arithm(x, "+", y, ">=", n).post()
    total = model.intvar(0, 2 * n, name="total")
    model.sum([x, y], "=", total).post()
    return model, {"x": x, "y": y}, ("minimize", total)
