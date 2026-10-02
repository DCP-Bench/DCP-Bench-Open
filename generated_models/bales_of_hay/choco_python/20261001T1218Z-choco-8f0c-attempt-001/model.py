# Bales of hay: bales were weighed in every combination of two and the weights
# were written down in numerical order; recover the weight of each bale.
from pychoco.model import Model

# Bounds the reference model declares (they belong to the problem, not the instance).
MAX_BALE_WEIGHT = 50
MAX_PAIR_WEIGHT = 100


def build(instance):
    n = instance["n"]  # number of bales
    weights = instance["weights"]  # the weights of all pairs of bales, without knowing which pair is which

    model = Model()

    # bales[i] = weight of bale i
    bales = [model.intvar(0, MAX_BALE_WEIGHT, name=f"bales_{i}") for i in range(n)]

    # the weight of every pair of bales is the sum of the two bales
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pair_weight = []
    for i, j in pairs:
        weight = model.intvar(0, MAX_PAIR_WEIGHT, name=f"pair_weight_{i}_{j}")
        model.arithm(bales[i], "+", bales[j], "=", weight).post()
        pair_weight.append(weight)

    # each written-down weight belongs to its own pair: the pair weights are exactly
    # the written-down weights, in some order. Putting the pair weights in increasing
    # order has to give the written-down list in increasing order (sort has no
    # auxiliary choice of "which pair is which", so the solver does not enumerate one).
    written_down = [model.intvar(w, w) for w in sorted(weights)]
    model.sort(pair_weight, written_down).post()

    return model, {"bales": bales}
