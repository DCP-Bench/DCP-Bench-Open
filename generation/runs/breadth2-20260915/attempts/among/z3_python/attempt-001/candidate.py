import z3

# The reference's own domain for x.
LOW, HIGH = 0, 7


def build(instance):
    n, wanted, values = instance["n"], instance["m"], instance["v"]
    x = [z3.Int(f"x_{i}") for i in range(n)]
    constraints = [v >= LOW for v in x] + [v <= HIGH for v in x]
    matches = [z3.If(x[i] == value, 1, 0) for i in range(n) for value in values]
    constraints.append(z3.Sum(matches) == wanted)
    return constraints, {"x": x}
