# Giant cat army riddle: start from [0] and extend the list by adding 5, adding
# 7 or taking a square root, so that all numbers are different integers of at
# most 60, the list contains 2, then 10, then 14 (in that order), and it ends
# with 14 after exactly 24 numbers.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# The riddle fixes these numbers, so they are mirrored here.
MAX_VALUE = 60  # largest number allowed in the list
LENGTH = 24  # number of entries in the list
GOAL = 14  # the last entry


def build(instance):
    pool = IDPool()
    # x[i] = the i-th number of the list; the direct encoding has one literal per value
    x = [Integer(f"x_{i}", 0, MAX_VALUE, vpool=pool) for i in range(LENGTH)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # all numbers are different
    engine.add_alldifferent(x)
    cnf = engine.clausify()

    # the list starts with 0 and ends with 14
    cnf.append([x[0].equals(0)])
    cnf.append([x[LENGTH - 1].equals(GOAL)])

    # each number follows the previous one by adding 5, adding 7, or taking the
    # square root (the previous number is the square of the next one): if the
    # i-th number is v, the next one is one of v + 5, v + 7 and the s with s * s = v
    for i in range(LENGTH - 1):
        for v in range(MAX_VALUE + 1):
            successors = [w for w in (v + 5, v + 7) if w <= MAX_VALUE]
            root = int(v ** 0.5)
            if root * root == v:
                successors.append(root)
            cnf.append([-x[i].equals(v)] + [x[i + 1].equals(w) for w in successors])

    # the list contains 2 and later 10: 10 appears, and wherever it does, 2 comes earlier
    cnf.append([x[j].equals(10) for j in range(LENGTH)])
    for j in range(1, LENGTH):
        cnf.append([-x[j].equals(10)] + [x[i].equals(2) for i in range(1, j)])

    return cnf, {"x": x}
