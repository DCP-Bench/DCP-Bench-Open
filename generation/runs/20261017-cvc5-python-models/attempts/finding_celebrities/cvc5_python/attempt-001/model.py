# Finding celebrities at a party (DCP-Bench problem finding_celebrities).
# graph[i][j] == 1 means guest i knows guest j. A celebrity is a guest that everybody
# at the party knows but that only knows other celebrities. At least one celebrity is
# present. Output: celebrities[i] is true when guest i is a celebrity.
import cvc5.pythonic as cz


def build(instance):
    graph = instance["graph"]
    n = len(graph)
    c = [cz.Bool(f"c_{i}") for i in range(n)]
    constraints = []

    # At least one celebrity is present at the party.
    if n == 1:
        constraints.append(c[0])
    else:
        constraints.append(cz.Or(c))

    # A celebrity is a guest that everybody at the party knows.
    for i in range(n):
        for j in range(n):
            if graph[j][i] != 1:
                constraints.append(cz.Not(c[i]))

    # but that only knows other celebrities.
    for i in range(n):
        for j in range(n):
            if graph[i][j] == 1:
                constraints.append(cz.Implies(c[i], c[j]))

    return constraints, {"celebrities": c}
