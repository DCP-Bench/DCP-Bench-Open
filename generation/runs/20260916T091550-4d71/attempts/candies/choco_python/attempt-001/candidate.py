from pychoco.model import Model


def build(instance):
    """Candies: every child gets at least one candy, and between neighbours the
    higher-rated child gets strictly more.  Minimize the total handed out.
    """
    ratings = instance["ratings"]
    n = len(ratings)

    model = Model()
    # Bounds follow the reference: at least one and at most n candies each.
    x = [model.intvar(1, n, name=f"x{i}") for i in range(n)]
    total = model.intvar(1, n * n, name="z")

    model.sum(x, "=", total).post()
    model.arithm(total, ">=", n).post()

    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            model.arithm(x[i - 1], ">", x[i]).post()
        elif ratings[i - 1] < ratings[i]:
            model.arithm(x[i - 1], "<", x[i]).post()

    return model, {"z": total, "x": x}, ("minimize", total)
