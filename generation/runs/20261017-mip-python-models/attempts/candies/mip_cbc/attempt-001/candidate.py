# Candies: give each child at least one candy, a child with a higher rating
# than an immediate neighbour gets more candies than that neighbour, and the
# total number of candies is minimised.
import mip


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i] = number of candies for child i. Each child gets at least 1 candy.
    # The upper bound n comes from the instance: in an optimal distribution a
    # child needs at most as many candies as there are children.
    x = [model.add_var(f"x_{i}", lb=1, ub=n, var_type=mip.INTEGER) for i in range(n)]

    # z = total number of candies
    z = model.add_var("z", lb=0, ub=n * n, var_type=mip.INTEGER)

    # the total number of candies is the sum of the candies of all children
    model += z == mip.xsum(x)

    # neighbours with different ratings: the child with the higher rating gets more candies
    # (neighbours with equal ratings have no constraint)
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            model += x[i] >= x[i + 1] + 1
        elif ratings[i] < ratings[i + 1]:
            model += x[i + 1] >= x[i] + 1

    # the objective is the total number of candies, to be minimised
    model.objective = z

    return model, {"x": x, "z": z}
