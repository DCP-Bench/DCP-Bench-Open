import cpmpy as cp


def build(instance):
    n, adjacency = instance["n"], instance["adj"]
    chosen = cp.boolvar(shape=n, name="c")
    model = cp.Model()
    for i in range(n):
        for j in range(i + 1, n):
            if adjacency[i][j] == 0:
                model += chosen[i] + chosen[j] <= 1
    model.maximize(cp.sum([chosen[i] for i in range(n)]))
    return model, {"c": [chosen[i] for i in range(n)]}
