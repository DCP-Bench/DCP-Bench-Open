"""Feasibility check and objective for graph colouring. A solution is {"colour": [c per node]}."""


def feasible(instance, solution):
    n = instance["n_nodes"]
    c = solution.get("colour")
    if not isinstance(c, list) or len(c) != n or any(type(x) is not int or x < 0 for x in c):
        return [f"'colour' must be a list of {n} non-negative integers"]
    return [f"edge {a}-{b}: both nodes have colour {c[a]}" for a, b in instance["edges"] if c[a] == c[b]]


def objective(instance, solution):
    return len(set(solution["colour"]))
