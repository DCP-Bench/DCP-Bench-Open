# Broken weights: a weight of m pounds broke into n pieces of whole-pound weights
# so that, on a balance scale, every whole weight from 1 to m can be weighed.
import z3


def build(instance):
    m = instance["m"]  # total weight of the original weight
    n = instance["n"]  # number of pieces

    # weights[j] is the weight of piece j, between 1 and m pounds.
    weights = [z3.Int(f"weights_{j}") for j in range(n)]
    # x[i][j] says where piece j goes when weighing the object of i + 1 pounds:
    # -1 = on the object's side of the scale, 0 = unused, 1 = on the other side.
    x = [[z3.Int(f"x_{i}_{j}") for j in range(n)] for i in range(m)]

    solver = z3.Solver()

    for w in weights:
        solver.add(w >= 1, w <= m)
    for row in x:
        for xij in row:
            solver.add(xij >= -1, xij <= 1)

    # The pieces together weigh m pounds.
    solver.add(z3.Sum(weights) == m)

    # Every weight from 1 to m can be weighed: some placement of the pieces on the
    # two sides makes their signed total equal to that weight. The signed piece
    # weight is written with If so that Z3 sees linear terms, not a product of
    # two variables.
    for i in range(m):
        signed = [z3.If(x[i][j] == 1, weights[j], z3.If(x[i][j] == -1, -weights[j], 0))
                  for j in range(n)]
        solver.add(z3.Sum(signed) == i + 1)

    return solver, {"weights": weights}
