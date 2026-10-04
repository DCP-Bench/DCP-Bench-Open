# Candies: give every child in a line at least one candy so that of two
# neighbours the one with the higher rating gets more, using as few candies
# in total as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    pool = IDPool()
    # x[i] is the number of candies child i gets: at least 1, and at most n,
    # the bound the reference declares (a strictly rising line of n children
    # needs n for the last one). Order encoding, because the neighbour
    # constraints are comparisons.
    x = [Integer(f"x{i}", 1, max(n, 2), encoding="order", vpool=pool) for i in range(n)]
    # z is the total number of candies. Every child gets at least one, so the
    # total is at least n (the reference states z >= n); n * n is the
    # reference's upper bound. Order encoding, so the objective below is one
    # weight-1 soft clause per threshold.
    z = Integer("z", n, n * n + 1, encoding="order", vpool=pool)
    engine = IntegerEngine(vars=x + [z], vpool=pool)

    # The domains above are widened by one value when n is 1, so no Integer
    # has a single value; these keep x within 1..n and z within n..n*n.
    for xi in x:
        engine.add_linear(xi <= n)
    engine.add_linear(z <= n * n)

    # z is the total number of candies.
    engine.add_linear(z - sum(x) == 0)

    # Of two neighbours, the child with the higher rating gets more candies.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            engine.add_linear(x[i - 1] - x[i] >= 1)
        elif ratings[i - 1] < ratings[i]:
            engine.add_linear(x[i] - x[i - 1] >= 1)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Minimise the total number of candies: every unit of z above its lower
    # bound n pays 1.
    for v in range(n + 1, n * n + 1):
        formula.append([-z.ge(v)], weight=1)

    return formula, {"z": z, "x": x}
