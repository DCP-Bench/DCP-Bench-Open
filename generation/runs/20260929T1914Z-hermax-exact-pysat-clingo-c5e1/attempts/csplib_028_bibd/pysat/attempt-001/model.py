# Balanced incomplete block design: arrange v objects into b blocks so that a
# block holds k objects, an object lies in r blocks, and any two distinct
# objects share exactly l blocks. Solved through the v x b incidence matrix.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    v, b, r, k, l = instance["v"], instance["b"], instance["r"], instance["k"], instance["l"]

    pool = IDPool()
    # matrix[i][j] is true when object i belongs to block j
    matrix = [[pool.id(("matrix", i, j)) for j in range(b)] for i in range(v)]

    cnf = CNF()
    # every object occurs in exactly r blocks (each row adds up to r)
    for i in range(v):
        cnf.extend(CardEnc.equals(lits=matrix[i], bound=r, vpool=pool, encoding=EncType.seqcounter).clauses)
    # every block contains exactly k objects (each column adds up to k)
    for j in range(b):
        cnf.extend(CardEnc.equals(lits=[matrix[i][j] for i in range(v)], bound=k, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # any two distinct objects occur together in exactly l blocks: the scalar
    # product of their rows is l. both is true exactly when both objects are in block j.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            together = []
            for j in range(b):
                both = pool.id(("both", i1, i2, j))
                cnf.append([-both, matrix[i1][j]])
                cnf.append([-both, matrix[i2][j]])
                cnf.append([both, -matrix[i1][j], -matrix[i2][j]])
                together.append(both)
            cnf.extend(CardEnc.equals(lits=together, bound=l, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"matrix": matrix}
