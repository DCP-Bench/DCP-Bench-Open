from pychoco.model import Model


def build(instance):
    """Schur's lemma: drop n balls into c boxes so that no box holds a triple
    x, y, z with x + y = z.
    """
    n = instance["n"]
    c = instance["c"]

    model = Model()
    balls = [model.intvar(1, c, name=f"b{i}") for i in range(n)]

    # Ball labels are 1-based, so ball k lives at balls[k - 1].  x and y may be
    # the same ball, in which case the first disjunct is simply unsatisfiable.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z > n:
                continue
            model.or_([
                model.arithm(balls[x - 1], "!=", balls[y - 1]),
                model.arithm(balls[x - 1], "!=", balls[z - 1]),
                model.arithm(balls[y - 1], "!=", balls[z - 1]),
            ]).post()

    return model, {"balls": balls}
