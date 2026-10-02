# Assignment with costs: give every task to a different person, at the lowest total cost.
# PySAT only decides satisfiability, so the total cost to minimise is returned as the
# objective (the runner refuses a returned objective instead of ignoring it).
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    cost = instance["cost"]  # cost[i][j] = cost of giving task i to person j
    rows, cols = len(cost), len(cost[0])

    pool = IDPool()
    cnf = CNF()
    # x[i][j] is true when task i is given to person j
    x = [[pool.id(("x", i, j)) for j in range(cols)] for i in range(rows)]

    # every task is given to exactly one person
    for i in range(rows):
        cnf.extend(CardEnc.equals(lits=x[i], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
    # a person gets at most one task
    for j in range(cols):
        cnf.extend(CardEnc.atmost(lits=[x[i][j] for i in range(rows)], bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    lits = [x[i][j] for i in range(rows) for j in range(cols)]
    weights = [cost[i][j] for i in range(rows) for j in range(cols)]
    return cnf, {"x": x}, ("minimize", lits, weights)
