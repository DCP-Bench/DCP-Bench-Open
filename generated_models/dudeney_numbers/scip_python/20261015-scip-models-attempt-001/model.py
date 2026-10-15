# Find a Dudeney number larger than 1: a perfect cube whose digit sum equals
# the cube root of the number, with at most n digits.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]
    m = Model()

    # the number has at most n digits, so it is below 10**n
    # the cube root r of the number is at most the largest r with r**3 < 10**n
    rmax = 0
    while (rmax + 1) ** 3 < 10 ** n:
        rmax += 1

    # b[v] = 1 if the cube root of the number is v (v >= 2, since the number is larger than 1)
    values = range(2, rmax + 1)
    b = {v: m.addVar(name=f"b_{v}", vtype="B") for v in values}
    m.addCons(quicksum(b[v] for v in values) == 1)

    # the cube root r is the chosen value
    r = m.addVar(name="r", vtype="I", lb=2, ub=rmax)
    m.addCons(r == quicksum(v * b[v] for v in values))

    # the digits of the number, from the least significant (d[0]) to the most (d[n-1])
    d = [m.addVar(name=f"d_{j}", vtype="I", lb=0, ub=9) for j in range(n)]

    # the number is the value of its digits
    number = quicksum(10 ** j * d[j] for j in range(n))

    # the number is a perfect cube: it equals v**3 for the chosen cube root v
    m.addCons(number == quicksum(v ** 3 * b[v] for v in values))

    # the digit sum of the number equals its cube root
    m.addCons(quicksum(d[j] for j in range(n)) == r)

    return m, {"number": number}
