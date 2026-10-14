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
    # Weighing a load with a piece multiplies the piece's weight by its side (-1, 0 or 1).
    # That is a product of variables, so a quadratic constraint that is not convex. CPLEX
    # accepts it only if the factors are binaries (it linearizes those products) and it is
    # told to search for a global optimum. So the weights are written in binary digits.
    model.parameters.optimalitytarget = 3

    # weights[j] is the weight of piece j, written in binary digits: bit[j, k] is the digit
    # worth 2**k. Enough digits to write the total weight m.
    digits = m.bit_length()
    bit = {(j, k): model.binary_var(name=f"bit_{j}_{k}") for j in range(n) for k in range(digits)}
    weights = [model.sum((2 ** k) * bit[j, k] for k in range(digits)) for j in range(n)]

    # Each piece weighs at least 1 pound and at most the total weight.
    for j in range(n):
        model.add_constraint(weights[j] >= 1)
        model.add_constraint(weights[j] <= m)

    # The pieces add up to the total weight.
    model.add_constraint(model.sum(weights) == m)

    # When weighing the load i + 1, piece j goes on the other side of the load (other[i, j]
    # is 1), on the load's side (same[i, j] is 1), or stays off the scale (both 0, or both 1
    # which cancels out). So the side of piece j is other[i, j] - same[i, j].
    other = {(i, j): model.binary_var(name=f"other_{i}_{j}") for i in range(m) for j in range(n)}
    same = {(i, j): model.binary_var(name=f"same_{i}_{j}") for i in range(m) for j in range(n)}

    # Every load from 1 to m can be weighed: the pieces on the other side minus those on the
    # load's side add up to the load.
    for i in range(m):
        model.add_constraint(
            model.sum(weights[j] * (other[i, j] - same[i, j]) for j in range(n)) == i + 1)

    return model, {"weights": weights}
