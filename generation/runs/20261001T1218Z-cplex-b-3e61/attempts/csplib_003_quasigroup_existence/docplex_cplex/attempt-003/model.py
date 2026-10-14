"""Quasigroup existence (QG3): an order-m quasigroup, i.e. an m-by-m Latin square over 0..m-1
read as a multiplication table, in which (a*b)*(b*a) = a for all elements a and b.

The model reports the multiplication table.
"""
from docplex.mp.model import Model


def build(instance):
    m = instance["m"]  # order of the quasigroup
    elems = range(m)

    model = Model("quasigroup_existence")
    # The QG3 rule below is stated with quadratic constraints over binaries, which are not
    # convex; CPLEX accepts them only when told to search for a global optimum.
    model.parameters.optimalitytarget = 3

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

    # QG3 property: (a*b)*(b*a) = a. Quadratic constraints count against the Community
    # Edition's 1000 constraints, so one per (a, a*b, b*a) (m^3 = 729 at m = 9) leaves no room.
    # The rule is stated with 2 * m^2 constraints instead, one pair per (u, w):
    #   meets(u, w) = number of pairs (a, b) with a*b = u and b*a = w, at most 1;
    #   first(u, w) = sum of a over those pairs, at most u*w.
    # The m^2 pairs (a, b) map into the m^2 pairs (u, w) at most once each, so every (u, w) is
    # met exactly once. Then the first(u, w) add up to m * (0 + ... + m-1), and so do the u*w
    # (every element appears m times in a Latin square); "at most" everywhere with equal
    # totals forces equality: the pair meeting (u, w) has a = u*w, which is the QG3 rule.
    for u in elems:
        for w in elems:
            pairs = [(a, b) for a in elems for b in elems]
            model.add_constraint(model.sum(is_[a, b, u] * is_[b, a, w] for a, b in pairs) <= 1)
            model.add_constraint(model.sum(a * is_[a, b, u] * is_[b, a, w] for a, b in pairs if a > 0)
                                 <= model.sum(a * is_[u, w, a] for a in elems))

    # Consequences of the QG3 property, stated linearly to help the search (they remove no
    # solution):
    # - with b = a: (a*a)*(a*a) = a, so if a*a = u then u*u = a;
    for a in elems:
        for u in elems:
            model.add_constraint(is_[a, a, u] <= is_[u, u, a])
    # - two different elements never commute: a*b = b*a = u for a != b would give
    #   a = u*u = b.
    for a in elems:
        for b in elems:
            if a < b:
                for u in elems:
                    model.add_constraint(is_[a, b, u] + is_[b, a, u] <= 1)

    quasigroup = [[model.sum(v * is_[a, b, v] for v in elems) for b in elems] for a in elems]
    return model, {"quasigroup": quasigroup}
