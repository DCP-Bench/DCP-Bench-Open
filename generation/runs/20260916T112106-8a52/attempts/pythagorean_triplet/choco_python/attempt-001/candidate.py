from pychoco.model import Model


def build(instance):
    """Pythagorean triplet: the one whose three members sum to 1000."""
    del instance

    model = Model()
    a = model.intvar(1, 500, name="a")
    b = model.intvar(1, 500, name="b")
    c = model.intvar(1, 500, name="c")

    model.scalar([a, b, c], [1, 1, 1], "=", 1000).post()

    # Choco squares through a dedicated constraint rather than an expression.
    aa = model.intvar(1, 500 * 500, name="aa")
    bb = model.intvar(1, 500 * 500, name="bb")
    cc = model.intvar(1, 500 * 500, name="cc")
    model.square(aa, a).post()
    model.square(bb, b).post()
    model.square(cc, c).post()
    model.scalar([aa, bb, cc], [1, 1, -1], "=", 0).post()

    return model, {"a": a, "b": b, "c": c}
