import cpmpy as cp


def build(instance):
    gates = instance["num_gates"]
    apples = cp.intvar(0, 100, shape=gates + 1, name="apples")
    model = cp.Model(apples[gates] == 1)
    for i in range(1, gates + 1):
        model += apples[i - 1] == 2 * (apples[i] + 1)
    return model, {"apples": [apples[i] for i in range(gates + 1)]}
