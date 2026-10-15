# Magic sequence of length n: x[i] is the number of times the value i occurs
# in the sequence x[0], ..., x[n-1].
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["n"]  # sequence length

    m = Model("magic_sequence")

    # x[i]: the i-th element of the sequence, between 0 and n-1
    x = [m.addVar(name=f"x_{i}", vtype="I", lb=0, ub=n - 1) for i in range(n)]

    # b[i, v] = 1 if element i takes the value v (one-hot encoding of x[i])
    b = {(i, v): m.addVar(name=f"b_{i}_{v}", vtype="B") for i in range(n) for v in range(n)}

    # each element takes exactly one value
    for i in range(n):
        # one value per element
        m.addCons(quicksum(b[i, v] for v in range(n)) == 1)
        # x[i] is the value chosen for element i
        m.addCons(x[i] == quicksum(v * b[i, v] for v in range(n)))

    # the value i occurs exactly x[i] times in the sequence
    for i in range(n):
        # count of value i equals x[i]
        m.addCons(quicksum(b[j, i] for j in range(n)) == x[i])

    # the counts add up to the length of the sequence
    m.addCons(quicksum(x) == n)

    m.setObjective(0, "minimize")
    return m, {"x": x}
