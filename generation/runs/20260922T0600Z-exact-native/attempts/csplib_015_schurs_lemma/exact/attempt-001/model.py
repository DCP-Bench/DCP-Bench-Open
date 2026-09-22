# Put balls 1..n into c boxes so no triple x + y = z shares a box.
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
    n = instance["n"]
    boxes = instance["c"]

    solver = Exact()
    balls = [f"ball{i}" for i in range(n)]
    for name in balls:
        solver.addVariable(name, 1, boxes)
    flags = {name: indicators(solver, name, 1, boxes) for name in balls}

    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z <= n:
                # No box holds all three at once.
                for box in range(1, boxes + 1):
                    solver.addConstraint(
                        [(1, flags[balls[x - 1]][box]),
                         (1, flags[balls[y - 1]][box]),
                         (1, flags[balls[z - 1]][box])], False, 0, True, 2)
    return solver, {"balls": balls}
