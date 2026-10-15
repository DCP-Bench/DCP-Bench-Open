# Find a 10 digit number using each digit 0 to 9 exactly once, where the
# number formed by its first n digits is divisible by n (n = 1..10).
from pyscipopt import Model, quicksum


def build(instance):
    # The problem has no instance fields; the sizes are fixed by the statement.
    ndig = 10
    m = Model()

    # x[i, v] = 1 if position i (from the left, 0-based) holds digit v
    x = {(i, v): m.addVar(name=f"x_{i}_{v}", vtype="B") for i in range(ndig) for v in range(10)}

    # each position holds exactly one digit
    for i in range(ndig):
        m.addCons(quicksum(x[i, v] for v in range(10)) == 1)

    # each digit is used exactly once
    for v in range(10):
        m.addCons(quicksum(x[i, v] for i in range(ndig)) == 1)

    # the number is a 10 digit number, so the leading digit is not 0
    m.addCons(x[0, 0] == 0)

    # d[i] = the digit at position i
    d = [m.addVar(name=f"d_{i}", vtype="I", lb=0, ub=9) for i in range(ndig)]
    for i in range(ndig):
        m.addCons(d[i] == quicksum(v * x[i, v] for v in range(10)))

    # prefix[n] = the number formed by the first n digits
    prefix = []
    for n in range(1, ndig + 1):
        prefix.append(quicksum(d[i] * 10 ** (n - 1 - i) for i in range(n)))

    # the number formed by the first n digits is divisible by n
    for n in range(1, ndig + 1):
        hi = (10 ** n - 1) // n
        q = m.addVar(name=f"q_{n}", vtype="I", lb=0, ub=hi)
        m.addCons(prefix[n - 1] == n * q)

    # the output is the full 10 digit number
    number = prefix[ndig - 1]
    return m, {"number": number}
