"""Feasibility check and objective for 0/1 knapsack. A solution is {"take": [0/1 per item]}."""


def feasible(instance, solution):
    n = len(instance["weights"])
    take = solution.get("take")
    if not isinstance(take, list) or len(take) != n or any(t not in (0, 1) or type(t) is bool for t in take):
        return [f"'take' must be a list of {n} values, each 0 or 1"]
    weight = sum(w * t for w, t in zip(instance["weights"], take))
    if weight > instance["capacity"]:
        return [f"total weight {weight} exceeds capacity {instance['capacity']}"]
    return []


def objective(instance, solution):
    return sum(v * t for v, t in zip(instance["values"], solution["take"]))
