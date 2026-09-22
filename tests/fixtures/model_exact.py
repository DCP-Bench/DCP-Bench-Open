from exact import Exact


def build(instance):
    n = instance["n"]
    solver = Exact()
    solver.addVariable("x", 0, n)
    solver.addVariable("y", 0, n)
    if not instance["optimize"]:
        solver.addConstraint([(1, "x"), (1, "y")], True, n, True, n)
        return solver, {"x": "x", "y": "y"}
    solver.addConstraint([(1, "x"), (1, "y")], True, n)
    return solver, {"x": "x", "y": "y"}, ("minimize", [(1, "x"), (1, "y")])
