# Ternary Steiner system of order n: find n*(n-1)/6 triples of the elements
# 1..n such that any two triples have at most one element in common (n must be
# 1 or 3 modulo 6).
from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]  # number of elements
    n_sets = n * (n - 1) // 6  # number of triples

    model = cp_model.CpModel()

    # sets[i][j] is true when element j belongs to triple i
    sets = [[model.new_bool_var(f"sets_{i}_{j}") for j in range(n)] for i in range(n_sets)]

    # every triple has exactly three elements
    for i in range(n_sets):
        model.add(sum(sets[i]) == 3)

    # two triples share at most one element. common[j] is forced true when
    # element j is in both triples, and at most one of them may be true; forcing
    # it only from below is enough because the count is bounded from above.
    for i1 in range(n_sets):
        for i2 in range(i1 + 1, n_sets):
            common = []
            for j in range(n):
                both = model.new_bool_var(f"common_{i1}_{i2}_{j}")
                model.add_bool_or([sets[i1][j].negated(), sets[i2][j].negated(), both])
                common.append(both)
            model.add(sum(common) <= 1)

    return model, {"sets": sets}
