"""Celebrities: find the people everybody knows and who know only other celebrities; there is at least one."""
from docplex.mp.model import Model


def build(instance):
    graph = instance["graph"]  # graph[i][j] is 1 if person i knows person j (everyone knows themselves)
    n = len(graph)
    people = range(n)
    known_by = [sum(graph[j][i] for j in people) for i in people]  # how many people know i
    knows = [sum(graph[i][j] for j in people) for i in people]     # how many people i knows

    model = Model("finding_celebrities")

    # celebrities[i] is 1 when person i is a celebrity.
    celebrities = model.binary_var_list(n, name="celebrities")

    # count[c] is 1 when there are exactly c celebrities, c in 1..n: at least one
    # is present.
    count = {c: model.binary_var(name=f"count_{c}") for c in range(1, n + 1)}
    model.add_constraint(model.sum(count.values()) == 1, ctname="one_count")
    model.add_constraint(model.sum(celebrities) == model.sum(c * count[c] for c in count), ctname="counted")

    # A person is a celebrity exactly when everybody knows them and the number of
    # people they know equals the number of celebrities. Both counts are data, so
    # the first condition is settled here and the second is one equality.
    for i in people:
        if known_by[i] == n and 1 <= knows[i] <= n:
            model.add_constraint(celebrities[i] == count[knows[i]], ctname=f"celebrity_{i}")
        else:
            celebrities[i].ub = 0

    return model, {"celebrities": celebrities}
