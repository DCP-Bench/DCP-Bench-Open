"""Celebrities: find the people everybody knows and who know only other celebrities; there is at least one."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    graph = instance["graph"]  # graph[i][j] is 1 if person i knows person j (everyone knows themselves)
    n = len(graph)
    people = range(n)
    known_by = [sum(graph[j][i] for j in people) for i in people]  # how many people know i
    knows = [sum(graph[i][j] for j in people) for i in people]     # how many people i knows

    model = gp.Model("finding_celebrities")

    # celebrities[i] is 1 when person i is a celebrity.
    celebrities = model.addVars(people, vtype=GRB.BINARY, name="celebrities")

    # count[c] is 1 when there are exactly c celebrities, c in 1..n: at least one
    # is present.
    count = model.addVars(range(1, n + 1), vtype=GRB.BINARY, name="count")
    model.addConstr(count.sum() == 1, name="one_count")
    model.addConstr(celebrities.sum() == gp.quicksum(c * count[c] for c in count), name="counted")

    # A person is a celebrity exactly when everybody knows them and the number of
    # people they know equals the number of celebrities. Both counts are data, so
    # the first condition is settled here and the second is one indicator.
    for i in people:
        if known_by[i] == n and 1 <= knows[i] <= n:
            model.addConstr(celebrities[i] == count[knows[i]], name=f"celebrity[{i}]")
        else:
            celebrities[i].UB = 0

    return model, {"celebrities": [celebrities[i] for i in people]}
