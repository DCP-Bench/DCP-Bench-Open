import z3


def build(instance):
    weights, capacity = instance["weights"], instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)
    bins = [z3.Int(f"bin_{j}") for j in range(n)]
    constraints = [b >= 0 for b in bins] + [b <= num_bins - 1 for b in bins]
    for i in range(n):
        constraints.append(
            z3.Sum([weights[j] * z3.If(bins[j] == i, 1, 0) for j in range(n)]) <= capacity)
    return constraints, {"bins": bins}
