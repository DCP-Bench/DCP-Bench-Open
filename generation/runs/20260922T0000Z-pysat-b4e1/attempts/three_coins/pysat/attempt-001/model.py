# Flip one coin per move so that all coins end up alike.
from dcp_sat import Sat


def build(instance):
    init = instance["init"]
    num_moves = instance["num_moves"]
    n = len(init)

    sat = Sat()
    steps = sat.bool_grid(num_moves + 1, n)
    for j in range(n):
        sat.clause([steps[0][j]] if init[j] else [-steps[0][j]])

    for row in range(1, num_moves + 1):
        changed = []
        for j in range(n):
            a, b, d = steps[row][j], steps[row - 1][j], sat.bool()
            # d <-> (a differs from b)
            sat.clause([-d, a, b])
            sat.clause([-d, -a, -b])
            sat.clause([d, -a, b])
            sat.clause([d, a, -b])
            changed.append(d)
        sat.exactly(changed, 1)

    # The last row is all heads or all tails, which is just "all equal".
    for j in range(1, n):
        sat.iff(steps[num_moves][0], steps[num_moves][j])
    return sat, {"steps": steps}
