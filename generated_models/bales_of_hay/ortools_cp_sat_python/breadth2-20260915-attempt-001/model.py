import itertools

from ortools.sat.python import cp_model

# The reference's own bound on a single bale.
HEAVIEST = 50


def build(instance):
    n, weights = instance["n"], instance["weights"]
    model = cp_model.CpModel()
    bales = [model.new_int_var(0, HEAVIEST, f"bale_{i}") for i in range(n)]
    pairs = list(itertools.combinations(range(n), 2))
    for position, weight in enumerate(weights):
        picks = []
        for i, j in pairs:
            pick = model.new_bool_var(f"pick_{position}_{i}_{j}")
            model.add(bales[i] + bales[j] == weight).only_enforce_if(pick)
            picks.append(pick)
        model.add_bool_or(picks)
    return model, {"bales": bales}
