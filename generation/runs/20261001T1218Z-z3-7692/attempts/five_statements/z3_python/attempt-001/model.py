# Five statements (Joyner): statement i says "exactly i of these five statements
# are false". Determine which statements are true.
import z3


def build(instance):
    del instance  # the puzzle states its own statements

    n = 5

    # statements[i] is True when statement i + 1 ("exactly i + 1 statements are
    # false") is true.
    statements = z3.BoolVector("statements", n)
    false_statements = [(z3.Not(s), 1) for s in statements]

    solver = z3.Solver()

    # Statement i + 1 is true exactly when precisely i + 1 of the five statements
    # are false.
    for i in range(n):
        solver.add(statements[i] == z3.PbEq(false_statements, i + 1))

    return solver, {"statements": list(statements)}
