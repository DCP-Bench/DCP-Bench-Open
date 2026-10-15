# Langford's problem: arrange two copies of each number 1..k in one sequence of
# 2k places so that the two copies of number i have exactly i numbers between them.
#
# Encoding: one-hot Bools first_<i>_<p>: the first copy of number i is at place p.
# The second copy then sits at place p + i + 1. Each place holds exactly one copy,
# and the number at a place is the integer expression sum(i * occupancy), used as
# the output sol.
from paramita.modelling import Bool


def build(instance):
    # k comes from the instance; the sequence has 2k places.
    k = instance["k"]
    n_places = 2 * k

    # first[i][p] = 1 when the first copy of number i is at place p (0-based).
    # The second copy of i needs place p + i + 1 inside the sequence, so p ends
    # at n_places - i - 2.
    first = {
        i: {p: Bool(f"first_{i}_{p}") for p in range(n_places - i - 1)}
        for i in range(1, k + 1)
    }
    cons = []

    # each number i has exactly one position for its first copy
    for i in range(1, k + 1):
        cons.append(sum(first[i].values()) == 1)

    # the two copies of number i have i numbers between them: the second copy is
    # at place p + i + 1 when the first is at p. occ[i][q] = 1 when a copy of
    # number i sits at place q: the first copy is at q, or the second copy is at q
    # (first copy at q - i - 1).
    occ = {i: {} for i in range(1, k + 1)}
    for i in range(1, k + 1):
        for q in range(n_places):
            terms = []
            if q in first[i]:
                terms.append(first[i][q])
            if q - i - 1 in first[i]:
                terms.append(first[i][q - i - 1])
            occ[i][q] = sum(terms) if terms else 0

    # each place of the sequence holds exactly one copy
    for q in range(n_places):
        cons.append(sum(occ[i][q] for i in range(1, k + 1)) == 1)

    # the number at each place, as an integer expression
    sol = [sum(i * occ[i][q] for i in range(1, k + 1)) for q in range(n_places)]

    return cons, {"sol": sol}
