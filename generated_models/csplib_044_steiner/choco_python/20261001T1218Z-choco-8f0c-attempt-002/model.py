# Ternary Steiner problem of order n: find n*(n-1)/6 triples of distinct elements out of
# 1..n such that any two triples have at most one element in common.
from pychoco.model import Model


def build(instance):
    n = instance["n"]  # order of the Steiner triple system (n mod 6 is 1 or 3)
    n_sets = n * (n - 1) // 6  # number of triples

    model = Model()

    # sets[i][j] is true when element j is part of triple i
    sets = [[model.boolvar(name=f"sets_{i}_{j}") for j in range(n)] for i in range(n_sets)]

    # every triple has exactly 3 elements
    for triple in sets:
        model.sum(triple, "=", 3).post()

    # Each triple is also written as its three elements in increasing order,
    # members[i][0] < members[i][1] < members[i][2], tied to the Booleans above.
    members = [[model.intvar(0, n - 1, name=f"members_{i}_{p}") for p in range(3)] for i in range(n_sets)]
    for i in range(n_sets):
        model.arithm(members[i][0], "<", members[i][1]).post()
        model.arithm(members[i][1], "<", members[i][2]).post()
        # is_member[p][k] is true when members[i][p] = k; the three positions hold
        # different elements, so element k is in the triple when one of them is k
        is_member = []
        for p in range(3):
            flags = [model.boolvar(name=f"is_member_{i}_{p}_{k}") for k in range(n)]
            model.bools_int_channeling(flags, members[i][p], 0).post()
            is_member.append(flags)
        for k in range(n):
            model.sum([is_member[p][k] for p in range(3)], "=", sets[i][k]).post()

    # Any two triples have at most one element in common. Seen from the elements, this
    # says that no pair of elements {a, b} lies in two triples (two triples sharing a and
    # b would have two common elements), i.e. the 3 pairs of every triple are all
    # different over all triples. A pair a < b is numbered a * n + b.
    pair_numbers = [a * n + b for a in range(n) for b in range(a + 1, n)]
    pairs = []
    for i in range(n_sets):
        for p, q in [(0, 1), (0, 2), (1, 2)]:
            pair = model.intvar(pair_numbers, name=f"pair_{i}_{p}{q}")
            model.scalar([members[i][p], members[i][q], pair], [n, 1, -1], "=", 0).post()
            pairs.append(pair)
    model.all_different(pairs).post()

    # Implied: when n*(n-1)/6 triples are chosen, their pairs are all the pairs of
    # elements, each once, and an element a occurs in (n-1)/2 triples, because the
    # n-1 pairs containing it are covered two at a time.
    if 3 * n_sets == n * (n - 1) // 2:
        for k in range(n):
            model.sum([sets[i][k] for i in range(n_sets)], "=", (n - 1) // 2).post()

    return model, {"sets": sets}
