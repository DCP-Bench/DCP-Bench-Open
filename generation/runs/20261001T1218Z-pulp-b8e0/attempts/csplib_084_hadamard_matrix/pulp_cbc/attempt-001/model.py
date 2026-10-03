"""Hadamard matrix (Legendre pairs): for an odd l, find two sequences a and b of l values,
each -1 or +1, that each sum to 1 and whose periodic autocorrelations add up to -2 at every
shift s = 1..(l-1)/2: PAF(a, s) + PAF(b, s) = -2, where PAF(a, s) is the sum over i of
a[i] * a[(i + s) mod l].

The model reports the two sequences.
"""
import pulp


def build(instance):
    l = instance["l"]  # odd length of each sequence
    half = (l - 1) // 2  # number of shifts constrained

    problem = pulp.LpProblem("hadamard_legendre_pairs", pulp.LpMinimize)  # satisfaction: no objective

    # A value -1 or +1 is a binary p: value = 2p - 1 (p = 1 for +1). The product of two
    # values is not linear, so it is written through unlike[i][j] = 1 if the two values
    # differ (p_i XOR p_j): the product is then 1 - 2 * unlike.
    p = {name: [pulp.LpVariable(f"{name}_{i}", cat="Binary") for i in range(l)] for name in "ab"}

    # each sequence sums to 1: (number of +1) - (number of -1) = 1, i.e. (l + 1) / 2 are +1
    for name in "ab":
        problem += pulp.lpSum(p[name]) == (l + 1) // 2

    # PAF(a, s) + PAF(b, s) = -2 for each shift s. PAF(x, s) = l - 2 * (number of i whose
    # value differs from that at i + s mod l), so the condition is: the numbers of
    # differing pairs in a and in b add up to l + 1.
    unlike = {}
    for s in range(1, half + 1):
        for name in "ab":
            for i in range(l):
                j = (i + s) % l
                q = pulp.LpVariable(f"unlike_{name}_{s}_{i}", cat="Binary")
                unlike[(name, s, i)] = q
                problem += q >= p[name][i] - p[name][j]
                problem += q >= p[name][j] - p[name][i]
                problem += q <= p[name][i] + p[name][j]
                problem += q <= 2 - p[name][i] - p[name][j]
        problem += pulp.lpSum(unlike[(name, s, i)] for name in "ab" for i in range(l)) == l + 1

    outputs = {name: [2 * var - 1 for var in p[name]] for name in "ab"}
    return problem, outputs
