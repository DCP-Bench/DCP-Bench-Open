# Largest set of mutually adjacent vertices.
from exact import Exact


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    solver = Exact()
    chosen = [f"c{i}" for i in range(n)]
    for name in chosen:
        solver.addVariable(name, 0, 1)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                solver.addConstraint([(1, chosen[i]), (1, chosen[j])],
                                     False, 0, True, 1)
    return solver, {"c": chosen}, ("maximize", [(1, name) for name in chosen])
