"""Candies: give every child at least one candy, with the higher-rated of two
neighbours getting more candies, and minimise the total number of candies.

Encoding: unary Bools b[i][k] meaning "child i gets more than k candies".
A child's candies are 1 + the number of true bits.
"""
from paramita.modelling import Bool, If


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)
    # a child never needs more than n candies in an optimal allocation
    top = n

    b = [[Bool(f"more_{i}_{k}") for k in range(1, top)] for i in range(n)]

    cons = []

    # unary order: a child with more than k+1 candies also has more than k
    for i in range(n):
        for k in range(1, top - 1):
            cons.append(If(b[i][k], b[i][k - 1]))

    # at least 1 candy for each child
    x = [1 + sum(b[i]) for i in range(n)]

    # the child with the higher rating of two neighbours gets more candies
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            cons.append(x[i] >= x[i + 1] + 1)
        elif ratings[i] < ratings[i + 1]:
            cons.append(x[i + 1] >= x[i] + 1)
        # equal ratings: neighbours have no constraint

    # minimise the total number of candies
    z = sum(x)
    return cons, {"x": x, "z": z}, ("minimize", z)
