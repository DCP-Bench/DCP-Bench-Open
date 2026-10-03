"""Five statements (Joyner): statement i says "exactly i of these statements are false"; which are true?"""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: five statements, as stated.
N = 5


def build(instance):
    model = gp.Model("five_statements")

    # statements[i] = 1 when statement i (counted from 0) is true.
    statements = [model.addVar(vtype=GRB.BINARY, name=f"statement[{i}]") for i in range(N)]

    # false_count[k] = 1 when exactly k statements are false.
    false_count = model.addVars(range(N + 1), vtype=GRB.BINARY, name="false_count")
    model.addConstr(false_count.sum() == 1, name="one_count")
    model.addConstr(gp.quicksum(k * false_count[k] for k in range(N + 1))
                    == N - gp.quicksum(statements), name="count_false")

    # Statement i is true exactly when i + 1 statements are false.
    for i in range(N):
        model.addConstr(statements[i] == false_count[i + 1], name=f"statement_meaning[{i}]")

    return model, {"statements": statements}
