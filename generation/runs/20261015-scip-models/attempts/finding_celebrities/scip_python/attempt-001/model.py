# Finding celebrities: a celebrity is known by everybody at the party and knows only other celebrities; at least one celebrity is present.
from pyscipopt import Model, quicksum


def build(instance):
    graph = instance["graph"]
    n = len(graph)
    m = Model()

    # c[i] = 1 if person i is a celebrity
    c = [m.addVar(name=f"c_{i}", vtype="B") for i in range(n)]

    # a celebrity is known by everybody at the party
    for i in range(n):
        for j in range(n):
            if j != i:
                # if j does not know i, then i is not a celebrity
                m.addCons(c[i] <= graph[j][i])

    # a celebrity only knows other celebrities
    for i in range(n):
        for j in range(n):
            if j != i and graph[i][j] == 1:
                # if i is a celebrity, then the guest i knows is a celebrity too
                m.addCons(c[i] <= c[j])

    # a person known by everybody and knowing only celebrities is a celebrity
    for i in range(n):
        if all(graph[j][i] == 1 for j in range(n) if j != i):
            known = [j for j in range(n) if j != i and graph[i][j] == 1]
            # c[i] = 1 when every guest that i knows is a celebrity
            m.addCons(c[i] + quicksum(1 - c[j] for j in known) >= 1)

    # at least one celebrity is present at the party
    # the sum of the celebrities is at least one
    m.addCons(quicksum(c) >= 1)

    # the output gives, for each person in the input order, whether they are a celebrity (0/1)
    return m, {"celebrities": c}
