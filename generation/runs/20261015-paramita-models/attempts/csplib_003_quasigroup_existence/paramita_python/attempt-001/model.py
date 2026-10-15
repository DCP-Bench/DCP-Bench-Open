"""csplib_003 quasigroup existence: an order-m Latin square with (a*b)*(b*a) = a (QG3.m).

A quasigroup of order m is an m x m table in which every element 0..m-1 occurs once in
each row and each column. The QG3 property requires (a*b)*(b*a) = a for all a and b.
"""
from paramita.modelling import Bool, And, If


def build(instance):
    m = instance["m"]

    # x[a][b][c] = the product a*b is c (one-hot over 0..m-1)
    x = [[[Bool(f"prod_{a}_{b}_{c}") for c in range(m)] for b in range(m)] for a in range(m)]

    cons = []

    # each cell of the table holds exactly one element
    for a in range(m):
        for b in range(m):
            cons.append(sum(x[a][b]) == 1)

    # each element occurs exactly once in every row
    for a in range(m):
        for c in range(m):
            cons.append(sum(x[a][b][c] for b in range(m)) == 1)

    # each element occurs exactly once in every column
    for b in range(m):
        for c in range(m):
            cons.append(sum(x[a][b][c] for a in range(m)) == 1)

    # QG3 property: (a*b)*(b*a) = a for all a, b
    # with c = a*b and d = b*a, the product c*d must be a
    for a in range(m):
        for b in range(m):
            for c in range(m):
                for d in range(m):
                    cons.append(If(And(x[a][b][c], x[b][a][d]), x[c][d][a]))

    quasigroup = [[sum(c * x[a][b][c] for c in range(m)) for b in range(m)] for a in range(m)]
    return cons, {"quasigroup": quasigroup}
