# Candies: children stand in a line with ratings; each gets at least one candy, and a child
# rated higher than a neighbour must get more candies than that neighbour. The total number
# of candies is to be as small as possible.
# PySAT only decides satisfiability, so the total is returned as the objective (the runner
# refuses a returned objective instead of ignoring it).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    pool = IDPool()
    # x[i] = number of candies of child i (at least 1; at most n, as the reference declares)
    x = [Integer(f"x{i}", 1, n, vpool=pool) for i in range(n)]
    # z = total number of candies
    z = Integer("z", 1, n * n, vpool=pool)
    engine = IntegerEngine(vars=x + [z], vpool=pool)

    engine.add_linear(z - sum(x) == 0)
    engine.add_linear(z >= n)
    # a child rated higher than the child before gets more candies, and lower gets fewer
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            engine.add_linear(x[i - 1] - x[i] >= 1)
        elif ratings[i - 1] < ratings[i]:
            engine.add_linear(x[i] - x[i - 1] >= 1)

    return engine.clausify(), {"x": x, "z": z}, ("minimize", z)
