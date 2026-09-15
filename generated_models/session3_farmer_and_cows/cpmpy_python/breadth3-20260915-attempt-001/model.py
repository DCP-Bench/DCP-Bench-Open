import cpmpy as cp


def build(instance):
    cows, sons = instance["num_cows"], instance["num_sons"]
    per_son = instance["cows_per_son"]
    milk = list(range(1, cows + 1))
    share = sum(milk) // sons
    assignment = cp.intvar(0, sons - 1, shape=cows, name="cow_assignments")
    model = cp.Model()
    for son in range(sons):
        model += cp.sum([assignment[i] == son for i in range(cows)]) == per_son[son]
        model += cp.sum([milk[i] * (assignment[i] == son) for i in range(cows)]) == share
    return model, {"cow_assignments": [assignment[i] for i in range(cows)]}
