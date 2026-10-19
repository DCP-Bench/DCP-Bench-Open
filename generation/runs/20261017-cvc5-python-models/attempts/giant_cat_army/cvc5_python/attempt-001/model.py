# giant_cat_army: a list of 24 distinct integers, each at most 60, built from [0].
# Each step adds 5, adds 7, or takes the square root of a perfect square.
# The list ends with 14, and 2, 10, 14 appear in that order.
import cvc5.pythonic as cz


def build(instance):
    n = 24
    x = [cz.Int(f"x{i}") for i in range(n)]
    cons = []

    # The list starts with 0 and ends with 14.
    # The list has 24 elements.
    cons.append(x[0] == 0)
    cons.append(x[n - 1] == 14)

    # All the elements are integers, distinct, and at most 60.
    for v in x:
        cons.append(v >= 0)
        cons.append(v <= 60)
    cons.append(cz.Distinct(x))

    # Starting with 0, you build the list by one of three operations:
    # adding 5, adding 7, or taking the square root.
    # The square root applies only to a perfect square; the root is an integer.
    for i in range(n - 1):
        steps = [x[i + 1] == x[i] + 5, x[i + 1] == x[i] + 7]
        for k in range(8):  # k * k <= 60 gives k <= 7
            steps.append(cz.And(x[i] == k * k, x[i + 1] == k))
        cons.append(cz.Or(steps))

    # The list has 2, 10 and 14 in that order, with other numbers allowed between them.
    pairs = [cz.And(x[p] == 2, x[q] == 10) for p in range(n) for q in range(p + 1, n)]
    cons.append(cz.Or(pairs))

    return cons, {"x": x}
