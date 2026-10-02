# Age changing: starting from my age and applying the four operations +2, /8, -3, *7, each once and
# in some order, gives my husband's age. Starting from his age and applying the same four
# operations in a different order gives my age. Find both ages.
from itertools import permutations

from exact import Exact


def build(instance):
    # This problem has no instance data. The four operations and the age range 16..120 belong to
    # the problem statement and the reference.
    n = 4  # number of operations: 0 = +2, 1 = /8, 2 = -3, 3 = *7
    age_low, age_high = 16, 120
    big = 8000  # larger than any difference between values 1..1000 produced by an operation

    solver = Exact()

    # m = my age, h = my husband's age
    solver.addVariable("m", age_low, age_high)
    solver.addVariable("h", age_low, age_high)

    # hlist: from my age (hlist[0] = m) to my husband's age (hlist[n] = h);
    # mlist: from my husband's age (mlist[0] = h) to my age (mlist[n] = m). Intermediate values
    # are between 1 and 1000 as in the reference.
    hlist = ["m"] + [f"hlist_{i}" for i in range(1, n)] + ["h"]
    mlist = ["h"] + [f"mlist_{i}" for i in range(1, n)] + ["m"]
    for i in range(1, n):
        solver.addVariable(hlist[i], 1, 1000)
        solver.addVariable(mlist[i], 1, 1000)

    # The order of the operations is a permutation of 0..3, one for each chain. There are only
    # 4! = 24 orders, so each chain picks one with a 0/1 variable per order; the operation used at
    # step i is then read off as a sum of those variables.
    orders = list(permutations(range(n)))
    choice = {}
    for chain in ("perm1", "perm2"):
        choice[chain] = [f"{chain}_is_{k}" for k in range(len(orders))]
        for name in choice[chain]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in choice[chain]], True, 1, True, 1)

    # the two chains use different orders of the operations
    for k in range(len(orders)):
        solver.addConstraint([(1, choice["perm1"][k]), (1, choice["perm2"][k])],
                             False, 0, True, 1)

    # step i of a chain applies operation `op` to the previous value when uses[chain][i][op] = 1
    def check(chain, values):
        for i in range(n):
            for op in range(n):
                uses = f"{chain}_step_{i}_uses_{op}"
                solver.addVariable(uses, 0, 1)
                solver.addConstraint([(1, uses)] + [(-1, choice[chain][k])
                                                    for k, order in enumerate(orders)
                                                    if order[i] == op], True, 0, True, 0)
                old, new = values[i], values[i + 1]
                # linear form of each operation: left = right when the operation is used; the
                # constraint is switched off (relaxed by `big`) when it is not used
                left, right = {0: ([(1, new), (-1, old)], 2),  # new = old + 2
                               1: ([(8, new), (-1, old)], 0),  # 8 * new = old (old / 8)
                               2: ([(1, new), (-1, old)], -3),  # new = old - 3
                               3: ([(1, new), (-7, old)], 0)}[op]  # new = old * 7
                solver.addConstraint(left + [(big, uses)], False, 0, True, right + big)
                solver.addConstraint(left + [(-big, uses)], True, right - big)

    check("perm1", hlist)
    check("perm2", mlist)

    return solver, {"m": "m", "h": "h"}
