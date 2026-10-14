# Broken weights: a weight of m pounds broke into n pieces of whole-pound weights
# so that, on a balance scale, every whole weight from 1 to m can be weighed.
import functools
import operator

import z3


def build(instance):
    m = instance["m"]  # total weight of the original weight
    n = instance["n"]  # number of pieces

    # The piece weights are bit-vectors. Z3's integer solver is slow at finding values that
    # make many sums of unknown weights hit exact targets, while its bit-vector solver
    # (which turns the sums into Boolean circuits) handles that well. The width leaves
    # room for any signed total of the pieces without wrapping round.
    width = (n * m).bit_length() + 2

    def total(terms):
        return functools.reduce(operator.add, terms)

    # weights[j] is the weight of piece j, between 1 and m pounds.
    weights = [z3.BitVec(f"weights_{j}", width) for j in range(n)]
    # right[i][j] / left[i][j]: when weighing the object of i + 1 pounds, piece j is on
    # the scale's other side / on the object's side. (Neither: the piece is unused.)
    right = [[z3.Bool(f"right_{i}_{j}") for j in range(n)] for i in range(m)]
    left = [[z3.Bool(f"left_{i}_{j}") for j in range(n)] for i in range(m)]

    solver = z3.Solver()

    for w in weights:
        solver.add(z3.UGE(w, 1), z3.ULE(w, m))

    # The pieces together weigh m pounds.
    solver.add(total(weights) == m)

    # A piece cannot be on both sides at once.
    for i in range(m):
        for j in range(n):
            solver.add(z3.Not(z3.And(right[i][j], left[i][j])))

    # Every weight from 1 to m can be weighed: some placement of the pieces on the two
    # sides makes their signed total (other side counts plus, object's side counts minus)
    # equal to that weight.
    for i in range(m):
        signed = [z3.If(right[i][j], weights[j],
                        z3.If(left[i][j], -weights[j], z3.BitVecVal(0, width)))
                  for j in range(n)]
        solver.add(total(signed) == i + 1)

    # The declared output is the list of weights as integers.
    return solver, {"weights": [z3.BV2Int(w) for w in weights]}
