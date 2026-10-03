"""Quasigroup existence (QG3): an order-m quasigroup, i.e. an m-by-m Latin square over 0..m-1
read as a multiplication table, in which (a*b)*(b*a) = a for all elements a and b.

The model reports the multiplication table.
"""
from docplex.mp.model import Model


def build(instance):
    m = instance["m"]  # order of the quasigroup
    elems = range(m)

    model = Model("quasigroup_existence")
    # The QG3 rule below is a quadratic constraint over binaries, which is not convex; CPLEX
    # accepts it only when told to search for a global optimum.
    model.parameters.optimalitytarget = 3
    # This is a pure feasibility problem: ask the search to favour finding a solution.
    model.parameters.emphasis.mip = 1

    # is_[a, b, v] = 1 when a*b = v; every product has exactly one value.
    is_ = {(a, b, v): model.binary_var(name=f"is_{a}_{b}_{v}") for a in elems for b in elems for v in elems}
    for a in elems:
        for b in elems:
            model.add_constraint(model.sum(is_[a, b, v] for v in elems) == 1)

    # Each element occurs once in every row.
    for a in elems:
        for v in elems:
            model.add_constraint(model.sum(is_[a, b, v] for b in elems) == 1)

    # Each element occurs once in every column.
    for b in elems:
        for v in elems:
            model.add_constraint(model.sum(is_[a, b, v] for a in elems) == 1)

    # QG3 property: (a*b)*(b*a) = a. Whenever a*b = u and b*a = w, then u*w = a. For fixed a and
    # u only one b has a*b = u (rows are Latin), so summing over b keeps the left side 0 or 1:
    # one quadratic constraint per (a, u, w), m^3 in all, instead of m^4 linear implications
    # that would exceed the Community Edition's 1000 constraints.
    for a in elems:
        for u in elems:
            for w in elems:
                model.add_constraint(model.sum(is_[a, b, u] * is_[b, a, w] for b in elems) <= is_[u, w, a])

    # Consequences of the QG3 property, stated linearly to help the search (they remove no
    # solution):
    # - with b = a: (a*a)*(a*a) = a, so if a*a = u then u*u = a;
    for a in elems:
        for u in elems:
            model.add_constraint(is_[a, a, u] <= is_[u, u, a])
    # - (a*b, b*a) determines a = (a*b)*(b*a) and b = (b*a)*(a*b), so two different elements
    #   never commute: a*b = b*a = u for a != b would give a = u*u = b.
    for a in elems:
        for b in elems:
            if a < b:
                for u in elems:
                    model.add_constraint(is_[a, b, u] + is_[b, a, u] <= 1)

    quasigroup = [[model.sum(v * is_[a, b, v] for v in elems) for b in elems] for a in elems]
    return model, {"quasigroup": quasigroup}
