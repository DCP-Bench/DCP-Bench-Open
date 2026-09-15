import cpmpy as cp


def build(instance):
    weights, capacity = instance["weights"], instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)
    bins = cp.intvar(0, num_bins - 1, shape=n, name="bins")
    model = cp.Model()
    # The reference writes this constraint for every i in range(len(weights));
    # for a bin index beyond num_bins no item can be there and it is vacuous.
    for i in range(n):
        model += cp.sum([weights[j] * (bins[j] == i) for j in range(n)]) <= capacity
    return model, {"bins": [bins[j] for j in range(n)]}
