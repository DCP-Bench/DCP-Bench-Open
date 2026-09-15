import cpmpy as cp


def build(instance):
    """Frog circle: arrange cards 1..n around a circle so the frog, jumping
    from each card by the number written on it, lands on every card.
    """
    n = instance["n"]

    x = cp.intvar(1, n, shape=(n,), name="x")
    pos = cp.intvar(0, n - 1, shape=(n,), name="pos")
    visited = cp.intvar(1, n, shape=(n,), name="visited")

    model = cp.Model(
        cp.AllDifferent(x),
        cp.AllDifferent(pos),
        cp.AllDifferent(visited),
        # The frog starts on card 1, at position 0.
        x[0] == 1,
        pos[0] == 0,
        visited[0] == 1,
    )
    for i in range(1, n):
        # Jump clockwise by the number on the card just landed on.
        model += pos[i] == (pos[i - 1] + x[pos[i - 1]]) % n
        model += visited[i] == x[pos[i]]

    return model, {"x": x}
