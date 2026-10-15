# Find the Pythagorean triplet a < b < c of natural numbers with a^2 + b^2 = c^2 and a + b + c = 1000.
from pyscipopt import Model


def build(instance):
    m = Model()
    # the triplet's sides; each is at most 998 because the other two sides are at least 1
    a = m.addVar(name="a", vtype="I", lb=1, ub=998)
    b = m.addVar(name="b", vtype="I", lb=1, ub=998)
    c = m.addVar(name="c", vtype="I", lb=1, ub=998)

    # the three numbers form a Pythagorean triplet: a^2 + b^2 = c^2
    m.addCons(a * a + b * b == c * c)

    # the perimeter of the triangle is 1000
    m.addCons(a + b + c == 1000)

    # order the sides so that a < b < c (the triplet is unique, so this only names it)
    m.addCons(a + 1 <= b)
    m.addCons(b + 1 <= c)

    # the output gives the three sides in order
    return m, {"a": a, "b": b, "c": c}
