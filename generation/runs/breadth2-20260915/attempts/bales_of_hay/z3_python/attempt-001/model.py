import itertools

import z3

# The reference's own bound on a single bale.
HEAVIEST = 50


def build(instance):
    n, weights = instance["n"], instance["weights"]
    bales = [z3.Int(f"bale_{i}") for i in range(n)]
    constraints = [b >= 0 for b in bales] + [b <= HEAVIEST for b in bales]
    for weight in weights:
        constraints.append(z3.Or([bales[i] + bales[j] == weight
                                  for i, j in itertools.combinations(range(n), 2)]))
    return constraints, {"bales": bales}
