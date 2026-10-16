# Peculiar number: find a number p between 1 and 10000 such that p + 1 is a
# square and p / 2 + 1 is also a square (48 is one such number).
import math

from pyscipopt import Model

# the search range from the problem statement (problem constant, not instance data)
LOWER = 1
UPPER = 10000


def build(instance):
    m = Model()

    # the peculiar number, between 1 and 10000
    p = m.addVar(name="peculiar", vtype="I", lb=LOWER, ub=UPPER)
    # h is half of p; the statement's "half" only makes sense when p is even
    h = m.addVar(name="half", vtype="I", lb=0, ub=UPPER // 2)
    # s and t are the square roots in the two conditions
    s = m.addVar(name="root_plus_one", vtype="I", lb=0, ub=math.isqrt(UPPER + 1))
    t = m.addVar(name="root_half_plus_one", vtype="I", lb=0, ub=math.isqrt(UPPER // 2 + 1))

    # p is even, so that its half h is an integer
    m.addCons(p == 2 * h)
    # the half of the number plus one is a square: h + 1 = t^2
    m.addCons(h + 1 == t * t)
    # the number plus one is a square: p + 1 = s^2
    m.addCons(p + 1 == s * s)

    # the statement asks for another number, so 48 itself is excluded: p != 48,
    # as a binary b that selects p >= 49 (b = 1) or p <= 47 (b = 0)
    b = m.addVar(name="above_48", vtype="B")
    m.addConsIndicator(p >= 49, binvar=b)
    m.addConsIndicator(p <= 47, binvar=b, activeone=False)

    # the output is the peculiar number
    return m, {"peculiar": p}
