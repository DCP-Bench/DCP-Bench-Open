"""Joyner's five statements: statement k says "exactly k of these statements are false",
for k = 1..5. Which statements are true?
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data: five statements.
    n = 5
    model = Model("five_statements")

    # statements[i] is 1 when statement i + 1 is true.
    statements = [model.binary_var(name=f"statement_{i + 1}") for i in range(n)]

    # Statement i + 1 is true exactly when i + 1 statements are false, that is when
    # n - (i + 1) statements are true.
    for i in range(n):
        model.add_equivalence(statements[i], model.sum(statements) == n - (i + 1))

    return model, {"statements": statements}
