from pychoco.model import Model


def build(instance):
    """All-interval series: a permutation of the pitch classes whose successive
    absolute differences are themselves all distinct.
    """
    n = instance["n"]

    model = Model()
    x = [model.intvar(0, n - 1, name=f"x{i}") for i in range(n)]
    diffs = [model.intvar(1, n - 1, name=f"d{i}") for i in range(n - 1)]

    model.all_different(x).post()
    model.all_different(diffs).post()
    for i in range(n - 1):
        model.distance(x[i + 1], x[i], "=", diffs[i]).post()

    return model, {"x": x, "diffs": diffs}
