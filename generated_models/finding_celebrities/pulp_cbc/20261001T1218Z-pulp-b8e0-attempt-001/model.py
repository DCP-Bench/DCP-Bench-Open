"""Finding celebrities: at a party, graph[i][j] = 1 if person i knows person j. A celebrity
is a person that everybody at the party knows and that knows only celebrities; at least
one celebrity is present.

The model reports, for each person, whether they are a celebrity.
"""
import pulp


def build(instance):
    graph = instance["graph"]  # graph[i][j] = 1 if person i knows person j
    n = len(graph)

    problem = pulp.LpProblem("finding_celebrities", pulp.LpMinimize)  # satisfaction: no objective

    # celebrities[i] = 1 if person i is a celebrity
    celebrities = [pulp.LpVariable(f"celebrities_{i}", cat="Binary") for i in range(n)]

    # num_celebrities is the number of celebrities, between 1 and n; count_is[v] = 1 if it is v
    count_is = {v: pulp.LpVariable(f"count_is_{v}", cat="Binary") for v in range(1, n + 1)}
    problem += pulp.lpSum(count_is.values()) == 1
    problem += pulp.lpSum(celebrities) == pulp.lpSum(v * count_is[v] for v in range(1, n + 1))

    # Person i is a celebrity if and only if everybody knows i (the column of the graph
    # adds up to n) and i knows exactly num_celebrities people (the row adds up to
    # num_celebrities). Both sums come from the data, so the condition on the row is the
    # indicator count_is[row sum] and the condition on the column is fixed.
    for i in range(n):
        known_by = sum(graph[j][i] for j in range(n))
        knows = sum(graph[i][j] for j in range(n))
        if known_by == n and 1 <= knows <= n:
            problem += celebrities[i] == count_is[knows]
        else:
            problem += celebrities[i] == 0

    return problem, {"celebrities": celebrities}
