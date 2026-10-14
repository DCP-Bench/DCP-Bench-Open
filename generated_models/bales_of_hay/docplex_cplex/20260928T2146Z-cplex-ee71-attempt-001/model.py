"""Bales of hay: recover the weight of each bale from the unlabelled weights of every pair of bales."""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]
    weights = instance["weights"]  # the written-down pair weights, in no particular order
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    written = range(len(weights))

    model = Model("bales_of_hay")

    # bales[i] is the weight of bale i; the reference model declares 0..50,
    # so every pair weighs at most 100, as its pair weights allow.
    bales = model.integer_var_list(n, 0, 50, name="bales")

    # matches[k, p] is 1 when written weight k is the weight of pair p.
    matches = model.binary_var_matrix(written, range(len(pairs)), name="matches")

    # Every written weight belongs to exactly one pair, and no pair takes two
    # written weights: each weight was recorded for a pair of its own.
    for k in written:
        model.add_constraint(model.sum(matches[k, p] for p in range(len(pairs))) == 1, ctname=f"weight_{k}")
    for p in range(len(pairs)):
        model.add_constraint(model.sum(matches[k, p] for k in written) <= 1, ctname=f"pair_{p}")

    # A written weight matched to a pair is that pair's total weight.
    for k in written:
        for p, (i, j) in enumerate(pairs):
            model.add_indicator(matches[k, p], bales[i] + bales[j] == weights[k], name=f"weighs_{k}_{p}")

    return model, {"bales": bales}
