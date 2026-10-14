"""Three coins: starting from the given faces, flip exactly one coin per move so that after
num_moves moves the coins show all heads or all tails.
"""
from docplex.mp.model import Model


def build(instance):
    num_moves = instance["num_moves"]
    init = instance["init"]  # 1 is tails, 0 is heads
    n = len(init)
    coins = range(n)

    model = Model("three_coins")

    # steps[m][j] is 1 when coin j shows tails after m moves.
    steps = [[model.binary_var(name=f"coin_{j}_after_{m}") for j in coins]
             for m in range(num_moves + 1)]

    # The coins start as given.
    for j in coins:
        model.add_constraint(steps[0][j] == init[j])

    # Each move flips exactly one coin. flipped is 1 when coin j changes in move m, which
    # for 0/1 values is |after - before|.
    for m in range(1, num_moves + 1):
        flipped = []
        for j in coins:
            f = model.binary_var(name=f"flip_{j}_in_{m}")
            before, after = steps[m - 1][j], steps[m][j]
            model.add_constraint(f >= after - before)
            model.add_constraint(f >= before - after)
            model.add_constraint(f <= after + before)
            model.add_constraint(f <= 2 - after - before)
            flipped.append(f)
        model.add_constraint(model.sum(flipped) == 1)

    # At the end the coins are all heads (sum 0) or all tails (sum n).
    all_tails = model.binary_var(name="all_tails")
    model.add_constraint(model.sum(steps[num_moves]) == n * all_tails)

    return model, {"steps": steps}
