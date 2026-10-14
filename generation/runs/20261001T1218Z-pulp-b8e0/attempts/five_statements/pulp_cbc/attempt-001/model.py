"""Five statements: statement i says "exactly i of these statements are false", for i = 1..5.
Determine which statements are true.

The model reports each statement as 0 (false) or 1 (true).
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    n = 5
    problem = pulp.LpProblem("five_statements", pulp.LpMinimize)  # satisfaction

    statements = [pulp.LpVariable(f"statement_{i}", cat="Binary") for i in range(n)]

    # false_count[k] = 1 if exactly k statements are false (one k holds)
    false_count = [pulp.LpVariable(f"false_count_{k}", cat="Binary") for k in range(n + 1)]
    problem += pulp.lpSum(false_count) == 1
    problem += n - pulp.lpSum(statements) == pulp.lpSum(k * var for k, var in enumerate(false_count))

    # statement i is true exactly when i + 1 statements are false
    for i in range(n):
        problem += statements[i] == false_count[i + 1]

    return problem, {"statements": statements}
