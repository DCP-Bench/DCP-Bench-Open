# Broken weights: a weight of m pounds broke into n pieces of whole-pound
# weights. Find piece weights that let a balance scale weigh every whole weight
# from 1 to m, where a piece may go on the same pan as the object, on the other
# pan, or stay off the scale.
from exact import Exact


def build(instance):
    m = instance["m"]  # weight of the unbroken weight
    n = instance["n"]  # number of pieces

    solver = Exact()
    # weights[j] = the weight of piece j
    weights = [f"weights_{j}" for j in range(n)]
    for name in weights:
        solver.addVariable(name, 1, m)

    # the pieces together weigh m
    solver.addConstraint([(1, name) for name in weights], True, m, True, m)

    # every weight 1..m can be weighed. Each piece is placed on one pan (+1), the
    # other pan (-1) or not used (0); its signed weight is weight * side, a
    # product of two variables that Exact multiplies natively.
    for target in range(1, m + 1):
        signed = []
        for j in range(n):
            side = f"side_{target}_{j}"
            term = f"term_{target}_{j}"
            solver.addVariable(side, -1, 1)
            solver.addVariable(term, -m, m)
            solver.addMultiplication([weights[j], side], True, term, True, term)
            signed.append((1, term))
        solver.addConstraint(signed, True, target, True, target)

    return solver, {"weights": weights}
