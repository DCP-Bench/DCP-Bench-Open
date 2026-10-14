# Curious set of integers: find a number x >= 0 that can be added to the set
# {1, 3, 8, 120} so that the product of any two integers in the set is one less
# than a perfect square.
import math

from pyscipopt import Model

# the given set of the problem statement (problem constant, not instance data)
GIVEN_SET = [1, 3, 8, 120]


def build(instance):
    # the search range for the fifth number comes from the instance
    max_val = instance["max_val"]

    m = Model()
    x = m.addVar(name="number", vtype="I", lb=0, ub=max_val)

    # the fifth number x must satisfy: a * x + 1 is a perfect square, for each
    # given integer a. Products of the given integers among themselves already
    # have this property, so only the pairs (a, x) are constrained.
    # s[a] is the square root of a * x + 1, bounded by the largest possible value.
    s = {}
    for a in GIVEN_SET:
        root_ub = math.isqrt(a * max_val + 1)
        s[a] = m.addVar(name=f"root_{a}", vtype="I", lb=0, ub=root_ub)
        # a * x + 1 = s[a]^2
        m.addCons(a * x + 1 == s[a] * s[a])

    # the output is the fifth number
    return m, {"number": x}
