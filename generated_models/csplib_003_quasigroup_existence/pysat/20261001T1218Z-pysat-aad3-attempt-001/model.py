# Quasigroup existence, QG3.m: find an order m quasigroup (an m x m multiplication table in which
# every element occurs once in each row and each column) such that (a * b) * (b * a) = a for all
# elements a and b.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    m = instance["m"]  # order of the quasigroup; the elements are 0..m-1

    pool = IDPool()
    # quasigroup[a][b] = the product a * b
    quasigroup = [[Integer(f"q_{a}_{b}", 0, m - 1, vpool=pool) for b in range(m)] for a in range(m)]
    engine = IntegerEngine(vars=[cell for row in quasigroup for cell in row], vpool=pool)

    # each element occurs once in every row and once in every column
    for i in range(m):
        engine.add_alldifferent(quasigroup[i])
        engine.add_alldifferent([quasigroup[a][i] for a in range(m)])
    cnf = engine.clausify()

    # the QG3.m property (a * b) * (b * a) = a. The product (a * b) * (b * a) is a table lookup at
    # the position given by two table entries, so it is stated per pair of values: if a * b = i
    # and b * a = j then i * j = a.
    for a in range(m):
        for b in range(m):
            for i in range(m):
                for j in range(m):
                    cnf.append([-quasigroup[a][b].equals(i), -quasigroup[b][a].equals(j),
                                quasigroup[i][j].equals(a)])

    return cnf, {"quasigroup": quasigroup}
