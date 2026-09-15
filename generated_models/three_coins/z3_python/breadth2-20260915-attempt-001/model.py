import z3


def build(instance):
    initial, moves = instance["init"], instance["num_moves"]
    n = len(initial)
    steps = [[z3.Bool(f"s_{m}_{j}") for j in range(n)] for m in range(moves + 1)]
    constraints = [steps[0][j] == bool(initial[j]) for j in range(n)]
    for m in range(1, moves + 1):
        flips = [z3.If(steps[m][j] != steps[m - 1][j], 1, 0) for j in range(n)]
        constraints.append(z3.Sum(flips) == 1)
    last = z3.Sum([z3.If(steps[moves][j], 1, 0) for j in range(n)])
    constraints.append(z3.Or(last == 0, last == n))
    return constraints, {"steps": steps}
