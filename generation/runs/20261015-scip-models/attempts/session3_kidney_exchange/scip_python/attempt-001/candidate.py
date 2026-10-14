# Kidney exchange: choose which compatible donations to make so that anyone who
# gives a kidney receives one, no person receives more than one kidney, and the
# number of people who receive a kidney is maximised.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["num_people"]
    compatible = instance["compatible"]  # compatible[i]: people i can donate to (1-based)
    m = Model()

    # x[i, j] = 1 if person i donates a kidney to person j; only compatible pairs exist
    x = {}
    for i in range(n):
        for j in compatible[i]:
            if j - 1 != i:
                x[i, j - 1] = m.addVar(name=f"donates_{i}_{j - 1}", vtype="B")

    def gives(i):
        return quicksum(v for (a, _), v in x.items() if a == i)

    def receives(i):
        return quicksum(v for (_, b), v in x.items() if b == i)

    # no person donates more than one kidney
    for i in range(n):
        m.addCons(gives(i) <= 1)

    # no person receives more than one kidney
    for i in range(n):
        m.addCons(receives(i) <= 1)

    # anyone who gives a kidney must receive one
    for i in range(n):
        m.addCons(gives(i) <= receives(i))

    # maximise the number of people who receive a kidney
    m.setObjective(quicksum(x.values()), "maximize")

    # transplants[i][j] = 1 if person i donates to person j, 0 otherwise
    transplants = [[x.get((i, j), 0) for j in range(n)] for i in range(n)]
    return m, {"transplants": transplants}
