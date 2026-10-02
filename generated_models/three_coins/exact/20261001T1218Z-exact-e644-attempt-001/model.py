# Three coins: coins lie on a table, each heads (0) or tails (1). In exactly num_moves moves, each
# flipping one coin, bring them to all heads or all tails. Return the state of the coins after every move.
from exact import Exact


def build(instance):
    num_moves = instance["num_moves"]
    init = instance["init"]  # initial configuration, 1 = tails, 0 = heads
    n = len(init)

    solver = Exact()
    # steps[m][j] is the face of coin j after m moves (1 = tails, 0 = heads); row 0 is the start
    steps = [[f"steps_{m}_{j}" for j in range(n)] for m in range(num_moves + 1)]
    for row in steps:
        for name in row:
            solver.addVariable(name, 0, 1)

    # The first row is the initial configuration.
    for j in range(n):
        solver.addConstraint([(1, steps[0][j])], True, init[j], True, init[j])

    # Exactly one coin differs between consecutive rows. flipped[m][j] = 1 when coin j changes in
    # move m, i.e. flipped = steps[m-1][j] xor steps[m][j], written as four linear inequalities.
    for m in range(1, num_moves + 1):
        flipped = [f"flipped_{m}_{j}" for j in range(n)]
        for j in range(n):
            before, after, flip = steps[m - 1][j], steps[m][j], flipped[j]
            solver.addVariable(flip, 0, 1)
            solver.addConstraint([(1, flip), (-1, before), (-1, after)], False, 0, True, 0)  # flip <= before + after
            solver.addConstraint([(1, flip), (1, before), (1, after)], False, 0, True, 2)  # flip <= 2 - before - after
            solver.addConstraint([(1, flip), (-1, before), (1, after)], True, 0)  # flip >= before - after
            solver.addConstraint([(1, flip), (1, before), (-1, after)], True, 0)  # flip >= after - before
        solver.addConstraint([(1, flip) for flip in flipped], True, 1, True, 1)

    # The last row is either all heads or all tails: the number of tails is 0 or n.
    solver.addVariable("all_tails", 0, 1)
    solver.addConstraint([(1, name) for name in steps[num_moves]] + [(-n, "all_tails")],
                         True, 0, True, 0)

    return solver, {"steps": steps}
