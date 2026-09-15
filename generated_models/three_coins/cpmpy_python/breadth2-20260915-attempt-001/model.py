import cpmpy as cp


def build(instance):
    initial, moves = instance["init"], instance["num_moves"]
    n = len(initial)
    steps = cp.boolvar(shape=(moves + 1, n), name="x")
    model = cp.Model([steps[0, j] == bool(initial[j]) for j in range(n)])
    for m in range(1, moves + 1):
        model += cp.sum([steps[m, j] != steps[m - 1, j] for j in range(n)]) == 1
    last = cp.sum([steps[moves, j] for j in range(n)])
    model += (last == 0) | (last == n)
    return model, {"steps": [[steps[m, j] for j in range(n)] for m in range(moves + 1)]}
