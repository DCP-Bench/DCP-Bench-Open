# Pythagorean triplet: find natural numbers a, b, c with a^2 + b^2 = c^2 and a + b + c = 1000.
from exact import Exact


def build(instance):
    # This problem has no instance data. The sum 1000 and the range 1..500 belong to the problem
    # statement: no side of a triangle with perimeter 1000 can exceed 500.
    total = 1000
    upper = 500

    solver = Exact()
    for name in ("a", "b", "c"):
        solver.addVariable(name, 1, upper)

    # a + b + c = 1000
    solver.addConstraint([(1, "a"), (1, "b"), (1, "c")], True, total, True, total)

    # a^2 + b^2 = c^2. Exact's constraints are linear, so each square gets a variable of its own,
    # tied to its root with Exact's multiplication constraint (square = root * root).
    for name in ("a", "b", "c"):
        solver.addVariable(f"{name}_squared", 1, upper * upper)
        solver.addMultiplication([name, name], True, f"{name}_squared", True, f"{name}_squared")
    solver.addConstraint([(1, "a_squared"), (1, "b_squared"), (-1, "c_squared")],
                         True, 0, True, 0)

    return solver, {"a": "a", "b": "b", "c": "c"}
