# ISBN-13 validation and check digit calculation: fill the unknown digits (-1) of a 13-digit ISBN so that it is valid.
from pyscipopt import Model, quicksum


def build(instance):
    init = instance["isbn_init"]
    n = len(init)  # 13 digits
    m = Model()

    # each digit is 0..9; a given digit is fixed to its value, an unknown digit (-1) stays free
    x = []
    for i, d in enumerate(init):
        if d == -1:
            x.append(m.addVar(name=f"d[{i}]", vtype="I", lb=0, ub=9))
        else:
            x.append(m.addVar(name=f"d[{i}]", vtype="I", lb=d, ub=d))

    # an ISBN-13 must start with 978 or 979
    # (the prefix 97 is fixed by the problem, the next digit is 8 or 9)
    m.addCons(x[0] == 9)
    m.addCons(x[1] == 7)
    m.addCons(x[2] >= 8)
    m.addCons(x[2] <= 9)

    # the first 12 digits are multiplied alternately by 1 and 3 (starting with 1) and summed
    weighted = quicksum((1 if i % 2 == 0 else 3) * x[i] for i in range(n - 1))

    # the check digit is (10 - (sum % 10)) % 10, so the weighted sum plus the check digit is a multiple of 10
    # (k is the multiple, bounded by the largest possible sum of 12 digits plus 9)
    k = m.addVar(name="k", vtype="I", lb=0, ub=23)
    m.addCons(weighted + x[n - 1] == 10 * k)

    # outputs: the complete ISBN as a list of 13 integers
    return m, {"isbn": x}
