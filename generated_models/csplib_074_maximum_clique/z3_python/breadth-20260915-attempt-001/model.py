import z3


def build(instance):
    n, adjacency = instance["n"], instance["adj"]
    chosen = [z3.Bool(f"c_{i}") for i in range(n)]
    picked = [z3.If(chosen[i], 1, 0) for i in range(n)]
    constraints = [z3.Not(z3.And(chosen[i], chosen[j]))
                   for i in range(n) for j in range(i + 1, n) if adjacency[i][j] == 0]
    return constraints, {"c": chosen}, ("maximize", z3.Sum(picked))
