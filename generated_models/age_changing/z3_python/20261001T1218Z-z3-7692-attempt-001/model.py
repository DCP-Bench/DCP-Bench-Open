# Age changing: start with my age and apply the four operations +2, /8, -3, *7, each once and in
# some order; the result is my husband's age. Starting from his age and applying the same
# four operations in a different order gives my age. What are the two ages?
import z3


def build(instance):
    # Constants of the problem (the instance has no data): four operations, ages 16..120.
    n = 4
    # operation numbers: 0 is +2, 1 is /8, 2 is -3, 3 is *7
    age_low, age_high = 16, 120

    # m is my age, h is my husband's age.
    m = z3.Int("m")
    h = z3.Int("h")
    # perm1 is the order of the operations applied to my age, perm2 the order applied to his.
    perm1 = [z3.Int(f"perm1_{i}") for i in range(n)]
    perm2 = [z3.Int(f"perm2_{i}") for i in range(n)]
    # hlist is the age after each step starting from mine; mlist starting from his.
    mlist = [z3.Int(f"mlist_{i}") for i in range(n + 1)]
    hlist = [z3.Int(f"hlist_{i}") for i in range(n + 1)]

    def check(perm, old, new):
        """The operation `perm` takes the value `old` to the value `new`."""
        return [
            z3.Implies(perm == 0, new == old + 2),
            # Division by 8 is written as a multiplication, to avoid rounding of the division.
            z3.Implies(perm == 1, 8 * new == old),
            z3.Implies(perm == 2, new == old - 3),
            z3.Implies(perm == 3, new == old * 7),
        ]

    solver = z3.Solver()

    solver.add(m >= age_low, m <= age_high, h >= age_low, h <= age_high)
    for i in range(n):
        solver.add(perm1[i] >= 0, perm1[i] <= n - 1, perm2[i] >= 0, perm2[i] <= n - 1)
    for i in range(n + 1):
        solver.add(mlist[i] >= 1, mlist[i] <= 1000, hlist[i] >= 1, hlist[i] <= 1000)

    # Each order uses every operation once.
    solver.add(z3.Distinct(perm1))
    solver.add(z3.Distinct(perm2))

    # The two orders are different.
    solver.add(z3.Or([perm1[i] != perm2[i] for i in range(n)]))

    # Start with my age and apply the operations of perm1: the last value is his age.
    solver.add(hlist[0] == m)
    solver.add(h == hlist[n])

    # Start with his age and apply the operations of perm2: the last value is my age.
    solver.add(mlist[0] == h)
    solver.add(m == mlist[n])

    # The values follow the operations of the two orders.
    for i in range(n):
        solver.add(check(perm1[i], hlist[i], hlist[i + 1]))
        solver.add(check(perm2[i], mlist[i], mlist[i + 1]))

    return solver, {"m": m, "h": h}
