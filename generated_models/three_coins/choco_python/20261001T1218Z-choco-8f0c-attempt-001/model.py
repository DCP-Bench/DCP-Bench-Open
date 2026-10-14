# Three coins: from the initial faces, flip exactly one coin per move so that after the given number
# of moves all coins show heads or all show tails.
from pychoco.model import Model


def build(instance):
    num_moves = instance["num_moves"]
    init = instance["init"]  # initial faces, 1 = tails, 0 = heads
    n = len(init)

    model = Model()

    # steps[m][j] is true when coin j shows tails after move m (row 0 is the start)
    steps = [[model.boolvar(name=f"steps_{m}_{j}") for j in range(n)] for m in range(num_moves + 1)]

    # The coins start in the given configuration.
    for j in range(n):
        model.arithm(steps[0][j], "=", init[j]).post()

    # Each move flips exactly one coin.
    for m in range(1, num_moves + 1):
        flipped = [model.arithm(steps[m][j], "!=", steps[m - 1][j]).reify() for j in range(n)]
        model.sum(flipped, "=", 1).post()

    # At the end the coins are all heads (no tails) or all tails.
    tails = model.intvar(0, n, name="tails")
    model.sum(steps[num_moves], "=", tails).post()
    model.member(tails, [0, n]).post()

    return model, {"steps": steps}
