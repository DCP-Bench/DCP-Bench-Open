# Three coins: coins lie on a table in a given order of heads and tails. In exactly
# num_moves moves, each flipping one coin, make them all heads or all tails.
from hermax.model import Model


def build(instance):
    init = instance["init"]            # 1 = tails, 0 = heads
    num_moves = instance["num_moves"]
    n = len(init)

    m = Model()
    # steps[t][j] = coin j shows tails after move t (row 0 is the starting position)
    steps = m.bool_matrix("steps", num_moves + 1, n)

    # the coins start as given
    for j in range(n):
        m &= steps[0][j] if init[j] else ~steps[0][j]

    # each move flips exactly one coin: flip[t][j] says coin j differs between rows t - 1 and t
    for t in range(1, num_moves + 1):
        flip = m.bool_vector(f"flip_{t}", n)
        for j in range(n):
            a, b, f = steps[t - 1][j], steps[t][j], flip[j]
            m &= (~f | a | b)
            m &= (~f | ~a | ~b)
            m &= (f | ~a | b)
            m &= (f | a | ~b)
        m &= (sum(flip[j] for j in range(n)) == 1)

    # at the end the coins are all heads or all tails: no two coins differ
    for j in range(1, n):
        m &= (~steps[num_moves][0] | steps[num_moves][j])
        m &= (steps[num_moves][0] | ~steps[num_moves][j])

    return m, {"steps": steps}
