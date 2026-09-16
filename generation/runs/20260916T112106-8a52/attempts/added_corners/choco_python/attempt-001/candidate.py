from pychoco.model import Model


def build(instance):
    """Added corners: digits 1..8 around a ring, each square the sum of its two
    adjoining circles.
    """
    del instance

    n = 8
    model = Model()
    positions = [model.intvar(1, n, name=f"p{i}") for i in range(n)]
    model.all_different(positions).post()

    # Reading order: a b c / d _ e / f g h. Each of b, d, e and g is a square
    # flanked by two circles.
    for square, first, second in ((1, 0, 2), (3, 0, 5), (4, 2, 7), (6, 5, 7)):
        model.scalar(
            [positions[square], positions[first], positions[second]],
            [1, -1, -1], "=", 0,
        ).post()

    return model, {"positions": positions}
