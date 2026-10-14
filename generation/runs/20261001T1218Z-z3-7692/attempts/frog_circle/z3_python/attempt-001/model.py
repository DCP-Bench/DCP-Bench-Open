# Frog on a circle: the cards 1..n are put on a circle. The frog starts at card 1 and, from
# a card k, jumps k places clockwise. Find an arrangement in which the frog lands on every
# card.
import z3


def build(instance):
    n = instance["n"]  # number of cards and of places on the circle

    # x[p] is the card in place p. The cards are 1..n, each used once.
    x = [z3.Int(f"x_{p}") for p in range(n)]
    # succ[p] is the place the frog reaches when it jumps from place p: x[p] places
    # clockwise, wrapping around the circle.
    succ = [z3.Int(f"succ_{p}") for p in range(n)]
    # on[i][p] is true if the frog is in place p after i jumps.
    on = [[z3.Bool(f"on_{i}_{p}") for p in range(n)] for i in range(n)]

    solver = z3.Solver()

    # The cards are 1..n, all different.
    for p in range(n):
        solver.add(x[p] >= 1, x[p] <= n)
    solver.add(z3.Distinct(x))

    # The frog starts on card 1, which is placed in place 0.
    solver.add(x[0] == 1)

    # A jump from place p ends at place (p + x[p]) mod n. As p + x[p] < 2n, the modulo is
    # one subtraction, which avoids the modulo operator.
    for p in range(n):
        solver.add(succ[p] == z3.If(p + x[p] >= n, p + x[p] - n, p + x[p]))

    # The frog begins in place 0; every later position is the place reached by jumping
    # from the previous one. This is the reference's pos[i] == (pos[i-1] + x[pos[i-1]]) % n,
    # with the indexing by a variable replaced by a Boolean per (jump, place).
    for p in range(n):
        solver.add(on[0][p] == (p == 0))
    for i in range(1, n):
        for q in range(n):
            solver.add(on[i][q] == z3.Or([z3.And(on[i - 1][p], succ[p] == q) for p in range(n)]))

    # The frog is in exactly one place at every step.
    for i in range(n):
        solver.add(z3.PbEq([(on[i][p], 1) for p in range(n)], 1))

    # The frog lands on every card: the places visited after 0, 1, ..., n - 1 jumps are
    # all different, so each place is visited exactly once. (The cards visited are then
    # all different too, since the cards are all different.)
    for p in range(n):
        solver.add(z3.PbEq([(on[i][p], 1) for i in range(n)], 1))

    return solver, {"x": x}
