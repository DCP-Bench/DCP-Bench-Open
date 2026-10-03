"""Quasigroup existence, QG3.m: find a quasigroup of order m, that is an m x m multiplication
table (a Latin square) over the elements 0..m-1 in which every element occurs once in every
row and once in every column, and in which (a * b) * (b * a) = a for all elements a and b.

The model reports the table.
"""
import pulp


def build(instance):
    m = instance["m"]  # order of the quasigroup
    elements = range(m)

    problem = pulp.LpProblem("qg3", pulp.LpMinimize)  # satisfaction: no objective

    # The model works on pairs of cells. Write phi(a, b) = (a * b, b * a). The QG3 property
    # (a * b) * (b * a) = a, applied to (a, b) and to (b, a), says phi(phi(a, b)) = (a, b).
    # So a table is a QG3 table exactly when phi is a map on pairs with
    #   phi(a, b) = (k, l)  if and only if  phi(k, l) = (a, b)   (phi undoes itself), and
    #   phi(a, b) = (k, l)  if and only if  phi(b, a) = (l, k)   (both read the same cells),
    # and the first coordinates of phi form a Latin square.
    # maps[a, b, k, l] = 1 if phi(a, b) = (k, l). The two equivalences say the four entries
    # (a,b,k,l), (k,l,a,b), (b,a,l,k), (l,k,b,a) are equal, so they share one binary.
    shared = {}

    def maps(a, b, k, l):
        key = min((a, b, k, l), (k, l, a, b), (b, a, l, k), (l, k, b, a))
        if key not in shared:
            shared[key] = pulp.LpVariable("maps_%d_%d_%d_%d" % key, cat="Binary")
        return shared[key]

    # every pair of elements has exactly one image
    for a in elements:
        for b in elements:
            problem += pulp.lpSum(maps(a, b, k, l) for k in elements for l in elements) == 1

    # a * b = k exactly when phi(a, b) = (k, l) for some l
    def times_is(a, b, k):
        return pulp.lpSum(maps(a, b, k, l) for l in elements)

    for k in elements:
        # every element occurs once in every row
        for a in elements:
            problem += pulp.lpSum(times_is(a, b, k) for b in elements) == 1
        # every element occurs once in every column
        for b in elements:
            problem += pulp.lpSum(times_is(a, b, k) for a in elements) == 1

    quasigroup = [[pulp.lpSum(k * times_is(a, b, k) for k in elements) for b in elements]
                  for a in elements]
    return problem, {"quasigroup": quasigroup}
