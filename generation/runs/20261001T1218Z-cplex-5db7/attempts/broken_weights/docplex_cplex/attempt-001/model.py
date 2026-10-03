"""Broken weights: a measuring weight of m pounds broke into n pieces of whole-pound weights.

On a balance scale the pieces must be able to weigh every whole weight from 1 to m: each
piece goes on the object's side, on the other side, or stays off. The model finds the
weights of the n pieces.
"""
from docplex.mp.model import Model


def build(instance):
    m = instance["m"]  # total weight of the pieces
    n = instance["n"]  # number of pieces

    model = Model("broken_weights")
    # Weighing a load with a piece multiplies the piece's weight by its side (-1, 0 or 1),
    # a product of two variables. That is a quadratic constraint, which is not convex, and
    # CPLEX refuses it unless it is told to search for a global optimum.
    model.parameters.optimalitytarget = 3

    # weights[j] is the weight of piece j, at least 1 pound and at most the total weight.
    weights = [model.integer_var(1, m, name=f"weight_{j}") for j in range(n)]

    # side[i, j] says where piece j goes when weighing the load i + 1: -1 on the object's
    # side, 1 on the other side, 0 off the scale.
    side = {(i, j): model.integer_var(-1, 1, name=f"side_{i}_{j}")
            for i in range(m) for j in range(n)}

    # The pieces add up to the total weight.
    model.add_constraint(model.sum(weights) == m)

    # Every load from 1 to m can be weighed: the pieces on one side minus those on the
    # other side add up to the load.
    for i in range(m):
        model.add_constraint(model.sum(weights[j] * side[i, j] for j in range(n)) == i + 1)

    return model, {"weights": weights}
