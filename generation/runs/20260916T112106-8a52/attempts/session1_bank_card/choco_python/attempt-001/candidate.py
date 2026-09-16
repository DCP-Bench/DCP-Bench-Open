from pychoco.model import Model


def build(instance):
    """Bank card: a four-digit PIN abcd where cd is three times ab and da is
    twice bc.
    """
    del instance

    model = Model()
    digits = [model.intvar(0, 9, name=name) for name in "abcd"]
    a, b, c, d = digits

    model.all_different(digits).post()
    # 10c + d = 3 * (10a + b), and 10d + a = 2 * (10b + c).
    model.scalar([c, d, a, b], [10, 1, -30, -3], "=", 0).post()
    model.scalar([d, a, b, c], [10, 1, -20, -2], "=", 0).post()

    return model, {"a": a, "b": b, "c": c, "d": d}
