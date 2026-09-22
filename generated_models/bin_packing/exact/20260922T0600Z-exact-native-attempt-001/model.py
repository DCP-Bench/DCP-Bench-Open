# Assign each item to a bin without exceeding the bin capacity.
from exact import Exact


def indicators(solver, name, lo, hi):
    """0/1 variables, one per value, with y[v] == 1 exactly when name == v."""
    flags = {v: f"{name}_is_{v}" for v in range(lo, hi + 1)}
    for flag in flags.values():
        solver.addVariable(flag, 0, 1)
    solver.addConstraint([(1, f) for f in flags.values()], True, 1, True, 1)
    solver.addConstraint([(v, flags[v]) for v in flags] + [(-1, name)],
                         True, 0, True, 0)
    return flags



def build(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)

    solver = Exact()
    bins = [f"bin{j}" for j in range(n)]
    for name in bins:
        solver.addVariable(name, 0, num_bins - 1)
    # The capacity is per bin, so each item's bin has to be named.
    flags = {name: indicators(solver, name, 0, num_bins - 1) for name in bins}
    for b in range(num_bins):
        solver.addConstraint([(weights[j], flags[bins[j]][b]) for j in range(n)],
                             False, 0, True, capacity)
    return solver, {"bins": bins}
