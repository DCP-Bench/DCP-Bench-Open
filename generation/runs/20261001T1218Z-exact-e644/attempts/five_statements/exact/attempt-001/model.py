# Five statements: statement k says "exactly k of these statements are false", for k = 1..5.
# Decide which statements are true; a statement is true exactly when what it says holds.
from exact import Exact


def build(instance):
    # This problem has no instance data. The five statements belong to the problem statement.
    n = 5

    solver = Exact()
    # statements[i] = 1 when statement i+1 is true
    statements = [f"statements_{i}" for i in range(n)]
    for name in statements:
        solver.addVariable(name, 0, 1)

    # exactly_false[k] = 1 when exactly k of the statements are false (k = 0..5). Exactly one of
    # these holds, and the number of false statements is n minus the number of true ones.
    exactly_false = [f"exactly_{k}_false" for k in range(n + 1)]
    for name in exactly_false:
        solver.addVariable(name, 0, 1)
    solver.addConstraint([(1, name) for name in exactly_false], True, 1, True, 1)
    # number of true statements = n - (number of false statements)
    solver.addConstraint([(1, name) for name in statements] +
                         [(-(n - k), exactly_false[k]) for k in range(n + 1)], True, 0, True, 0)

    # Statement i+1 is true exactly when exactly i+1 statements are false.
    for i in range(n):
        solver.addConstraint([(1, statements[i]), (-1, exactly_false[i + 1])], True, 0, True, 0)

    return solver, {"statements": statements}
