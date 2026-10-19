# Candies: Alice gives at least 1 candy to each child in a line. Children with a
# higher rating than an immediate neighbour must get more candies than that
# neighbour. Minimise the total number of candies.
# Output the total (z) and the number of candies for each child (x).
import cvc5.pythonic as cz


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    x = [cz.Int(f"x_{i}") for i in range(n)]
    z = cz.Int("z")

    cons = []

    # Each child gets at least 1 candy.
    for xi in x:
        cons.append(xi >= 1)

    # If two children sit next to each other, then the one with the higher
    # rating must get more candies. Equal ratings give no constraint.
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            cons.append(x[i] > x[i + 1])
        elif ratings[i] < ratings[i + 1]:
            cons.append(x[i] < x[i + 1])

    # The total number of candies is the sum over all children.
    cons.append(z == cz.Sum(x))

    s = cz.SolverFor("QF_LIA")
    s.add(*cons)
    return s, {"x": x, "z": z}, ("minimize", z)
