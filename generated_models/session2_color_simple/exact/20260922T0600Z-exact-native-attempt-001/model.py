# Colour adjacent countries differently, using as few colours as possible.
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
    graph = instance["graph"]
    # The edge list numbers the countries 1..num_nodes.
    num_nodes = max(max(edge) for edge in graph)

    solver = Exact()
    colors = [f"col{i}" for i in range(num_nodes)]
    for name in colors:
        solver.addVariable(name, 1, num_nodes)
    # Two adjacent countries must not take the same value, which is the one
    # thing a linear constraint cannot say without indicators.
    flags = {name: indicators(solver, name, 1, num_nodes) for name in colors}
    for left, right in graph:
        a, b = colors[left - 1], colors[right - 1]
        for value in range(1, num_nodes + 1):
            solver.addConstraint([(1, flags[a][value]), (1, flags[b][value])],
                                 False, 0, True, 1)

    # Minimising an upper bound on every colour drives it to the largest one.
    solver.addVariable("used", 1, num_nodes)
    for name in colors:
        solver.addConstraint([(1, name), (-1, "used")], False, 0, True, 0)
    return solver, {"colors": colors}, ("minimize", [(1, "used")])
