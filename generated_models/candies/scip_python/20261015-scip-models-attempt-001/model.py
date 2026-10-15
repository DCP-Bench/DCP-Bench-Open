# Candies: give each child in a line at least 1 candy so that a child with a higher
# rating than an immediate neighbour gets more candies than that neighbour, while
# minimising the total number of candies.

from pyscipopt import Model, quicksum


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    m = Model()

    # x[i] = number of candies for child i; a child never needs more than n candies,
    # since the candies of a child are bounded by the length of the longest run of
    # increasing ratings ending at that child
    x = [m.addVar(name=f"x_{i}", vtype="I", lb=1, ub=n) for i in range(n)]

    # z = total number of candies
    z = m.addVar(name="z", vtype="I", lb=n, ub=n * n)

    # total candies is the sum of the candies of all children
    m.addCons(z == quicksum(x[i] for i in range(n)))

    # a child with a higher rating than the neighbour gets more candies than the neighbour
    # (the comparison is fixed by the ratings in the instance, so no indicator is needed)
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            m.addCons(x[i] >= x[i + 1] + 1)
        elif ratings[i] < ratings[i + 1]:
            m.addCons(x[i + 1] >= x[i] + 1)
        # equal neighbours have no constraint between them

    m.setObjective(z, "minimize")
    return m, {"x": x, "z": z}
