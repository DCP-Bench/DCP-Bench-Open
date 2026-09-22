# Put each person in a free interview slot, one person per slot.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    free = instance["m"]
    n = len(free)

    pool = IDPool()
    x = [[pool.id(("x", i, j)) for j in range(n)] for i in range(n)]
    cnf = CNF()
    for i in range(n):
        # the chosen slot must be one the person is free for
        for j in range(n):
            if not free[i][j]:
                cnf.append([-x[i][j]])
        cnf.extend(CardEnc.equals(lits=x[i], bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    for j in range(n):
        column = [x[i][j] for i in range(n)]
        cnf.extend(CardEnc.equals(lits=column, bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
    return cnf, {"x": x}
