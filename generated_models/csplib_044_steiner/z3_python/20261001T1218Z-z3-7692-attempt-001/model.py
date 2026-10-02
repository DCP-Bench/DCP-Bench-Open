# Ternary Steiner problem: find n * (n - 1) / 6 triples of distinct elements out of 1..n such
# that any two triples have at most one element in common (n mod 6 is 1 or 3).
import z3


def build(instance):
    n = instance["n"]                  # order of the Steiner triple system, n mod 6 in {1, 3}
    n_sets = n * (n - 1) // 6          # number of triples, from the problem statement

    # sets[i][j] is true if element j is part of triple i.
    sets = [[z3.Bool(f"sets_{i}_{j}") for j in range(n)] for i in range(n_sets)]

    solver = z3.Solver()

    # Every triple has exactly three elements.
    for s in sets:
        solver.add(z3.PbEq([(b, 1) for b in s], 3))

    # Any two triples have at most one element in common. This is stated per pair of elements:
    # two triples sharing both elements a and b would have two elements in common, so every
    # pair of elements lies together in at most one triple. The triples hold 3 pairs each,
    # n_sets * 3 = n * (n - 1) / 2, which is all the pairs of elements, so each pair lies
    # together in exactly one triple; stating the equality is stronger for Z3 than "at most".
    for a in range(n):
        for b in range(a + 1, n):
            together = [(z3.And(sets[i][a], sets[i][b]), 1) for i in range(n_sets)]
            solver.add(z3.PbEq(together, 1))

    return solver, {"sets": sets}
