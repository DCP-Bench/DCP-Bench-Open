# Quasigroup existence, QG3.m: fill an m by m table with the values 0..m-1 so that
# every value occurs once in every row and once in every column (a Latin square, the
# multiplication table of a quasigroup), and so that (a*b)*(b*a) = a for all a and b,
# where a*b is the entry in row a and column b.
import functools
import operator

from hermax.model import Model


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number.
    """
    if len(lits) == 1:
        m &= lits[0]
        return
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= functools.reduce(operator.or_, lits)


def build(instance):
    order = instance["m"]  # order of the quasigroup: the table is order by order

    m = Model()
    # is_value[a][b][c] = the entry in row a, column b is c
    is_value = [[m.bool_vector(f"is_value_{a}_{b}", order) for b in range(order)] for a in range(order)]
    # quasigroup[a][b] = the entry in row a, column b (the declared output). hermax needs
    # at least two values, so with order 1 the second value is ruled out.
    quasigroup = [[m.int(f"quasigroup_{a}_{b}", 0, max(order - 1, 1)) for b in range(order)]
                  for a in range(order)]
    if order == 1:
        m &= ~(quasigroup[0][0] >= 1)

    # every cell holds exactly one value
    for a in range(order):
        for b in range(order):
            exactly_one(m, [is_value[a][b][c] for c in range(order)], f"cell_{a}_{b}")
    # quasigroup shows the value held: holding c means quasigroup >= c and not
    # quasigroup >= c + 1 (comparisons outside the range 0..order-1 are settled)
    for a in range(order):
        for b in range(order):
            for c in range(order):
                if c > 0:
                    m &= (~is_value[a][b][c] | (quasigroup[a][b] >= c))
                if c < order - 1:
                    m &= (~is_value[a][b][c] | ~(quasigroup[a][b] >= c + 1))

    # each value occurs once in every row
    for a in range(order):
        for c in range(order):
            exactly_one(m, [is_value[a][b][c] for b in range(order)], f"row_{a}_{c}")
    # each value occurs once in every column
    for b in range(order):
        for c in range(order):
            exactly_one(m, [is_value[a][b][c] for a in range(order)], f"column_{b}_{c}")

    # The QG3.m property (a*b)*(b*a) = a. If a*b = c and b*a = d, then c*d = a:
    # (is_value[a][b][c] and is_value[b][a][d]) imply is_value[c][d][a].
    for a in range(order):
        for b in range(order):
            for c in range(order):
                for d in range(order):
                    m &= (~is_value[a][b][c] | ~is_value[b][a][d] | is_value[c][d][a])

    return m, {"quasigroup": quasigroup}
