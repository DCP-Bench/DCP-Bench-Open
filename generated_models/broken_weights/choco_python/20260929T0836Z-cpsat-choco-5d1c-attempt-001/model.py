# Broken weights: a weight of m pounds broke into n pieces of whole-pound
# weights. Find piece weights that let a balance scale weigh every whole weight
# from 1 to m, where a piece may go on the same pan as the object, on the other
# pan, or stay off the scale.
from pychoco.model import Model


def build(instance):
    m = instance["m"]  # weight of the unbroken weight
    n = instance["n"]  # number of pieces

    model = Model()

    # weights[j] = the weight of piece j
    weights = [model.intvar(1, m, name=f"weights_{j}") for j in range(n)]

    # the pieces together weigh m
    model.sum(weights, "=", m).post()

    # every weight 1..m can be weighed. Each piece is placed on one pan (+1),
    # the other pan (-1) or not used (0), and the signed weights add up to the
    # weight being measured.
    for target in range(1, m + 1):
        signed = []
        for j in range(n):
            side = model.intvar(-1, 1, name=f"side_{target}_{j}")
            term = model.intvar(-m, m, name=f"term_{target}_{j}")
            model.times(weights[j], side, term).post()
            signed.append(term)
        model.sum(signed, "=", target).post()

    return model, {"weights": weights}
