import cpmpy as cp


def build(instance):
    n, least, most = instance["n"], instance["m1"], instance["m2"]
    steps = cp.intvar(0, most, shape=n, name="steps")
    model = cp.Model(cp.sum([steps[i] for i in range(n)]) == n)
    for i in range(n):
        model += (steps[i] >= least) | (steps[i] == 0)
    for i in range(1, n):
        # Once a move is empty, every later one is too.
        model += (steps[i - 1] == 0).implies(cp.all([steps[j] == 0 for j in range(i, n)]))
    return model, {"steps": [steps[i] for i in range(n)]}
