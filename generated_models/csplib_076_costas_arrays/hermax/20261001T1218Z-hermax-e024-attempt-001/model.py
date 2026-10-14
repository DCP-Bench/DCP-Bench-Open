# Costas array: place n marks on an n x n grid, one per row and one per
# column, so that the vectors between all pairs of marks are different. As a
# permutation costas[0..n-1] of 1..n, the differences costas[i + l] - costas[i]
# must be pairwise different for every distance l.
from hermax.model import Model


def build(instance):
    n = instance["n"]

    m = Model()
    # costas[i] = the (1-based) column of the mark in row i (the declared output)
    costas = m.int_vector("costas", n, 1, n)
    # mark[i][a] = the mark of row i is in column a + 1 (one-hot form of costas)
    mark = m.bool_matrix("mark", n, n)

    # one mark per row and one per column, so costas is a permutation of 1..n
    for i in range(n):
        m &= mark.row(i).exactly_one()
        m &= mark.col(i).exactly_one()
    for i in range(n):
        for a in range(n):
            m &= (~mark[i][a] | (costas[i] == a + 1))

    # For each distance l, the differences costas[i + l] - costas[i] over all i
    # are pairwise different (a row of the difference triangle has no repeated
    # value). same[l][d][i] is forced true when row i + l minus row i has
    # difference d (d is stored shifted by n - 1); the difference d can be taken
    # by at most one i for each l. Only the forcing direction is needed, so the
    # check needs no equivalence and stays at about n^3 short clauses.
    for l in range(1, n - 1):  # l = n - 1 has a single difference, nothing to compare
        same = {d: m.bool_vector(f"same_{l}_{d + n - 1}", n - l) for d in range(-(n - 1), n)}
        for i in range(n - l):
            for a in range(n):
                for b in range(n):
                    if a != b:
                        m &= (~mark[i][a] | ~mark[i + l][b] | same[b - a][i])
        for d in range(-(n - 1), n):
            m &= same[d].at_most_one()

    return m, {"costas": costas}
