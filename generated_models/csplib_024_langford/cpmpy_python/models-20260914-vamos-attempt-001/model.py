import cpmpy as cp


def build(instance):
    k = instance["k"]
    # position[i - 1] and position[k + i - 1] hold the two places of value i.
    position = cp.intvar(0, 2 * k - 1, shape=2 * k, name="position")
    sol = cp.intvar(1, k, shape=2 * k, name="sol")
    model = cp.Model(cp.AllDifferent(position))
    for i in range(1, k + 1):
        model += position[i + k - 1] == position[i - 1] + i + 1
        model += sol[position[i - 1]] == i
        model += sol[position[k + i - 1]] == i
    return model, {"sol": [sol[j] for j in range(2 * k)]}
