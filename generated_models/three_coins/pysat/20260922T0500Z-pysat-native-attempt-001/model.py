# Flip one coin per move so that all coins end up alike.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    init = instance["init"]
    num_moves = instance["num_moves"]
    n = len(init)

    pool = IDPool()
    steps = [[pool.id(("s", r, j)) for j in range(n)] for r in range(num_moves + 1)]
    cnf = CNF()
    for j in range(n):
        cnf.append([steps[0][j]] if init[j] else [-steps[0][j]])

    for row in range(1, num_moves + 1):
        changed = []
        for j in range(n):
            a, b = steps[row][j], steps[row - 1][j]
            d = pool.id(("d", row, j))
            # d <-> (a differs from b)
            cnf.append([-d, a, b])
            cnf.append([-d, -a, -b])
            cnf.append([d, -a, b])
            cnf.append([d, a, -b])
            changed.append(d)
        cnf.extend(CardEnc.equals(lits=changed, bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # The last row is all heads or all tails, which is just "all equal".
    for j in range(1, n):
        cnf.append([-steps[num_moves][0], steps[num_moves][j]])
        cnf.append([steps[num_moves][0], -steps[num_moves][j]])
    return cnf, {"steps": steps}
