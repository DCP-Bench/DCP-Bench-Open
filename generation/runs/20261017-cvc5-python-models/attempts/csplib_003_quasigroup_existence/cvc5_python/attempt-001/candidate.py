# QG3.m quasigroup existence: find an order m quasigroup (a Latin square of size m,
# values 0..m-1) with (a*b)*(b*a) = a for all a, b.
import cvc5.pythonic as cz


def build(instance):
    m = instance["m"]
    rng = range(m)

    # The quasigroup: Q[i][j] is the product i*j, values 0..m-1.
    Q = [[cz.Int(f"q_{i}_{j}") for j in rng] for i in rng]

    constraints = []

    # Every value in 0..m-1 for each cell.
    for i in rng:
        for j in rng:
            constraints.append(Q[i][j] >= 0)
            constraints.append(Q[i][j] <= m - 1)

    # each element occurs once in every row and column of the multiplication table
    # (Distinct needs at least two terms, so a 1 x 1 table has nothing to separate)
    if m >= 2:
        for i in rng:
            constraints.append(cz.Distinct(Q[i]))
        for j in rng:
            constraints.append(cz.Distinct([Q[i][j] for i in rng]))

    # (a*b)*(b*a) = a for all a, b.
    # Let p = a*b and q = b*a. For every cell (i, j), if p == i and q == j then Q[i][j] == a.
    # This states (a*b)*(b*a) = a without a variable-index lookup.
    for a in rng:
        for b in rng:
            p = Q[a][b]
            q = Q[b][a]
            for i in rng:
                for j in rng:
                    constraints.append(cz.Or(p != i, q != j, Q[i][j] == a))

    return constraints, {"quasigroup": Q}
