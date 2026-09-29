# Ternary Steiner system of order n: find n*(n-1)/6 triples of the elements
# 1..n such that any two triples have at most one element in common (n must be
# 1 or 3 modulo 6).
from hermax.model import Model


def build(instance):
    n = instance["n"]  # number of elements
    n_sets = n * (n - 1) // 6  # number of triples

    m = Model()
    # sets[i][j] is true when element j belongs to triple i
    sets = m.bool_matrix("sets", n_sets, n)

    # every triple has exactly three elements
    for i in range(n_sets):
        m &= (sum(1 * sets[i][j] for j in range(n)) == 3)

    # Two triples share at most one element exactly when no pair of elements lies
    # in two triples. For each pair of elements, together[i] says triple i holds
    # both, and at most one triple does.
    for p in range(n):
        for q in range(p + 1, n):
            together = m.bool_vector(f"together_{p}_{q}", n_sets)
            for i in range(n_sets):
                m &= (~sets[i][p] | ~sets[i][q] | together[i])
            m &= together.at_most_one()

    return m, {"sets": sets}
