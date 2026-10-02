# Frog circle: place the cards 1..n around a circle so that a frog starting on card 1 and jumping,
# from card k, k places clockwise lands on every card of the circle.
from exact import Exact


def build(instance):
    n = instance["n"]

    solver = Exact()

    # card_is[p][v] = 1 when position p of the circle holds card v (v in 1..n). Positions are
    # numbered 0..n-1 clockwise; the cards form a permutation of 1..n, which is stated through
    # these indicators because Exact has no all-different constraint.
    card_is = [[f"position_{p}_holds_{v}" for v in range(1, n + 1)] for p in range(n)]
    for p in range(n):
        for name in card_is[p]:
            solver.addVariable(name, 0, 1)
        # every position holds exactly one card
        solver.addConstraint([(1, name) for name in card_is[p]], True, 1, True, 1)
    for v in range(n):
        # every card is placed exactly once
        solver.addConstraint([(1, card_is[p][v]) for p in range(n)], True, 1, True, 1)

    # x[p] is the card at position p
    x = [f"x_{p}" for p in range(n)]
    for p in range(n):
        solver.addVariable(x[p], 1, n)
        solver.addConstraint([(v, card_is[p][v - 1]) for v in range(1, n + 1)] + [(-1, x[p])],
                             True, 0, True, 0)

    # the frog starts on card 1 at position 0
    solver.addConstraint([(1, card_is[0][0])], True, 1, True, 1)

    # at_step[i][p] = 1 when the frog is at position p after i jumps. The visited positions must
    # all be different (n of them, so every card is visited): a permutation matrix again.
    at_step = [[f"step_{i}_at_position_{p}" for p in range(n)] for i in range(n)]
    for i in range(n):
        for name in at_step[i]:
            solver.addVariable(name, 0, 1)
        # at each step the frog is at exactly one position
        solver.addConstraint([(1, name) for name in at_step[i]], True, 1, True, 1)
    for p in range(n):
        # every position is visited at exactly one step
        solver.addConstraint([(1, at_step[i][p]) for i in range(n)], True, 1, True, 1)
    solver.addConstraint([(1, at_step[0][0])], True, 1, True, 1)

    # a jump: from position p holding card v the frog goes to position (p + v) mod n. As a clause,
    # "at p at step i and p holds v" implies "at (p + v) mod n at step i + 1".
    for i in range(n - 1):
        for p in range(n):
            for v in range(1, n + 1):
                solver.addConstraint([(-1, at_step[i][p]), (-1, card_is[p][v - 1]),
                                      (1, at_step[i + 1][(p + v) % n])], True, -1)

    return solver, {"x": x}
