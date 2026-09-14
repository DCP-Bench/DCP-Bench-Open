import z3


def build(instance):
    n = instance["n"]
    x = [z3.Int(f"x_{i}") for i in range(n)]
    constraints = [z3.And(value >= 0, value <= n - 1) for value in x]
    # Magic sequence: the value at position i is how often i occurs in x.
    # z3 has no Count, so sum a 0/1 indicator per position.
    for i in range(n):
        constraints.append(x[i] == z3.Sum([z3.If(value == i, 1, 0) for value in x]))
    return constraints, {"x": x}
