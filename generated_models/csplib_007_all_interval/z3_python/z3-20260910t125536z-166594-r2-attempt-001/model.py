import z3


def build(instance):
    n = instance["n"]
    x = [z3.Int(f"x_{i}") for i in range(n)]
    diffs = [z3.Int(f"diffs_{i}") for i in range(n - 1)]
    constraints = [z3.And(pitch >= 0, pitch <= n - 1) for pitch in x]
    constraints += [z3.And(step >= 1, step <= n - 1) for step in diffs]
    constraints.append(z3.Distinct(x))
    constraints.append(z3.Distinct(diffs))
    # Each interval is the absolute difference of successive pitch classes.
    for i in range(n - 1):
        constraints.append(diffs[i] == z3.Abs(x[i + 1] - x[i]))
    return constraints, {"x": x, "diffs": diffs}
