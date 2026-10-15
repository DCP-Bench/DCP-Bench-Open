# Five self-referential statements: statement i says "exactly i of these statements are false".
# Find which statements are true (1) and which are false (0).
from pyscipopt import Model, quicksum


def build(instance):
    n = 5  # the problem has five statements, fixed by the problem statement
    m = Model()

    # t[i] = 1 if statement i (1-based, "exactly i are false") is true
    t = {i: m.addVar(name=f"t_{i}", vtype="B") for i in range(1, n + 1)}

    # count of false statements, between 0 and n
    k = m.addVar(name="false_count", vtype="I", lb=0, ub=n)

    # one-hot encoding of the false count: y[v] = 1 iff exactly v statements are false
    y = {v: m.addVar(name=f"y_{v}", vtype="B") for v in range(0, n + 1)}
    # exactly one count value holds
    m.addCons(quicksum(y[v] for v in y) == 1)
    # the false count equals the value selected by the one-hot encoding
    m.addCons(k == quicksum(v * y[v] for v in y))

    # a statement is true exactly when the false count equals its index
    # (statement i is true iff exactly i statements are false)
    for i in range(1, n + 1):
        m.addCons(t[i] == y[i])

    # the false count is the number of statements that are false (not true)
    m.addCons(k == n - quicksum(t[i] for i in range(1, n + 1)))

    # output order follows the input: statement 1 ("exactly one is false") first
    statements = [t[i] for i in range(1, n + 1)]
    return m, {"statements": statements}
