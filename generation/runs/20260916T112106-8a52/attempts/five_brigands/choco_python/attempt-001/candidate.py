from pychoco.model import Model


def build(instance):
    """Five brigands: 200 doubloons shared so that the reweighted shares also
    come to 200.

    The reweighting is 12A + 3B + C + D/2 + E/3; multiplying through by six
    clears both fractions, which is what the reference does.
    """
    del instance

    model = Model()
    brigands = [model.intvar(1, 200, name=name) for name in "ABCDE"]
    a, b, c, d, e = brigands

    model.scalar(brigands, [1, 1, 1, 1, 1], "=", 200).post()
    model.scalar(brigands, [72, 18, 6, 3, 2], "=", 6 * 200).post()

    return model, {"A": a, "B": b, "C": c, "D": d, "E": e}
