# Find four different numbers a, b, c, d in 1..100 with a^2 + b^2 = c^2 + d^2.
from pyscipopt import Model, quicksum


def neq(m, x, y, name):
    # x != y, encoded with one binary that picks the side of the inequality
    d = m.addVar(name=name, vtype="B")
    m.addConsIndicator(x - y >= 1, binvar=d)
    m.addConsIndicator(y - x >= 1, binvar=d, activeone=False)


def build(instance):
    m = Model()
    # the four numbers, each between 1 and 100 (problem statement)
    a = m.addVar(name="a", vtype="I", lb=1, ub=100)
    b = m.addVar(name="b", vtype="I", lb=1, ub=100)
    c = m.addVar(name="c", vtype="I", lb=1, ub=100)
    d = m.addVar(name="d", vtype="I", lb=1, ub=100)
    nums = {"a": a, "b": b, "c": c, "d": d}

    # the four numbers are different (a != b != c != d, read as all pairwise different)
    names = list(nums)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p, q = names[i], names[j]
            neq(m, nums[p], nums[q], f"diff_{p}_{q}")

    # the sum of squares of the first two equals the sum of squares of the other two
    sq_a = m.addVar(name="sq_a", vtype="I", lb=1, ub=10000)
    sq_b = m.addVar(name="sq_b", vtype="I", lb=1, ub=10000)
    sq_c = m.addVar(name="sq_c", vtype="I", lb=1, ub=10000)
    sq_d = m.addVar(name="sq_d", vtype="I", lb=1, ub=10000)
    m.addCons(sq_a == a * a)
    m.addCons(sq_b == b * b)
    m.addCons(sq_c == c * c)
    m.addCons(sq_d == d * d)
    m.addCons(sq_a + sq_b == sq_c + sq_d)

    return m, {"a": a, "b": b, "c": c, "d": d}
