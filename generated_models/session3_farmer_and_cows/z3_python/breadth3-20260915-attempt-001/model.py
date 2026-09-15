import z3


def build(instance):
    cows, sons = instance["num_cows"], instance["num_sons"]
    per_son = instance["cows_per_son"]
    milk = list(range(1, cows + 1))
    share = sum(milk) // sons
    assignment = [z3.Int(f"a_{i}") for i in range(cows)]
    constraints = [a >= 0 for a in assignment] + [a <= sons - 1 for a in assignment]
    for son in range(sons):
        got = [z3.If(assignment[i] == son, 1, 0) for i in range(cows)]
        constraints.append(z3.Sum(got) == per_son[son])
        constraints.append(z3.Sum([milk[i] * got[i] for i in range(cows)]) == share)
    return constraints, {"cow_assignments": assignment}
