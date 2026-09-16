from pychoco.model import Model


def build(instance):
    """N queens: one queen per row, no two sharing a column or a diagonal."""
    n = instance["n"]

    model = Model()
    queens = [model.intvar(1, n, name=f"q{i}") for i in range(n)]
    model.all_different(queens).post()

    # Choco compares variables, not expressions, so the two diagonals get their
    # own variables tied to the queens with a scalar equality.
    down = []
    up = []
    for i in range(n):
        shifted_down = model.intvar(1 - n, n, name=f"down{i}")
        model.scalar([queens[i], shifted_down], [1, -1], "=", i).post()
        down.append(shifted_down)
        shifted_up = model.intvar(1, 2 * n, name=f"up{i}")
        model.scalar([queens[i], shifted_up], [1, -1], "=", -i).post()
        up.append(shifted_up)
    model.all_different(down).post()
    model.all_different(up).post()

    return model, {"queens": queens}
