from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
    if not instance["optimize"]:
        m &= (x + y == n)
        return m, {"x": x, "y": y}
    m &= (x + y >= n)
    m.obj += (x + y)
    return m, {"x": x, "y": y}
