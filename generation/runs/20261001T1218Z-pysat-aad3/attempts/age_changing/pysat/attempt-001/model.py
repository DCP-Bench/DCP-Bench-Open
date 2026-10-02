# Age changing: starting from my age and applying the four operations +2, /8, -3, *7 in some
# order gives my husband's age; starting from his age and applying the same four operations in
# a different order gives mine. What are the two ages?
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The four operations, each as the function that gives the new age from the old one, or None
    # when the operation does not apply. "/8" only applies when the old age is a multiple of 8
    # (the reference states it as 8 * new == old). These belong to the problem statement.
    operations = [
        lambda old: old + 2,
        lambda old: old // 8 if old % 8 == 0 else None,
        lambda old: old - 3,
        lambda old: old * 7,
    ]
    n = len(operations)
    age_low, age_high = 16, 120  # both ages lie in 16..120 (given by the problem)
    value_low, value_high = 1, 1000  # every age on the way lies in 1..1000 (given by the problem)

    pool = IDPool()
    m = Integer("m", age_low, age_high, vpool=pool)  # my age
    h = Integer("h", age_low, age_high, vpool=pool)  # my husband's age

    # perm1[i] / perm2[i] = the operation applied in step i, when starting from my age / his age
    perm1 = [Integer(f"perm1_{i}", 0, n - 1, vpool=pool) for i in range(n)]
    perm2 = [Integer(f"perm2_{i}", 0, n - 1, vpool=pool) for i in range(n)]

    # hlist[i] = the age after i steps when starting from my age. It starts at my age and ends at
    # my husband's age, so the first and last entries are the variables m and h themselves.
    hlist = [m] + [Integer(f"hlist{i}", value_low, value_high, vpool=pool) for i in range(1, n)] + [h]
    # mlist[i] = the age after i steps when starting from his age. It starts at his age and ends
    # at my age.
    mlist = [h] + [Integer(f"mlist{i}", value_low, value_high, vpool=pool) for i in range(1, n)] + [m]

    ages = list(dict.fromkeys(hlist + mlist))
    engine = IntegerEngine(vars=ages + perm1 + perm2, vpool=pool)

    # each of the two sequences uses every operation exactly once
    engine.add_alldifferent(perm1)
    engine.add_alldifferent(perm2)

    cnf = engine.clausify()

    # the two sequences are different orders: some step uses a different operation
    differs = [pool.id(("differs", i)) for i in range(n)]
    cnf.append(differs)
    for i in range(n):
        for k in range(n):
            cnf.append([-differs[i], -perm1[i].equals(k), -perm2[i].equals(k)])

    # each step applies the chosen operation to the age before it to give the age after it.
    # PySAT has no division and multiplication of a variable by an operation chosen at solving
    # time, so every operation is listed value by value: the old age fixes the new one, and an
    # old age that the operation cannot take (or that leaves the allowed values) is excluded.
    def apply_step(perm, old, new):
        for k, operation in enumerate(operations):
            for value in range(old.lb, old.ub + 1):
                result = operation(value)
                if result is not None and new.lb <= result <= new.ub:
                    cnf.append([-perm.equals(k), -old.equals(value), new.equals(result)])
                else:
                    cnf.append([-perm.equals(k), -old.equals(value)])

    for i in range(n):
        apply_step(perm1[i], hlist[i], hlist[i + 1])
        apply_step(perm2[i], mlist[i], mlist[i + 1])

    return cnf, {"m": m, "h": h}
