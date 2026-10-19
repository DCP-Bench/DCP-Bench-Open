# Finding celebrities at a party (Python-MIP, CBC).
# Given a list of people at a party and for each person the list of people they
# know at the party, find the celebrities. A celebrity is a person that everybody
# at the party knows but that only knows other celebrities. At least one celebrity
# is present. Output: 0/1 per person, in the input order.
import mip


def build(instance):
    graph = instance["graph"]
    n = len(graph)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    c = [model.add_var(f"celebrity_{i}", var_type=mip.BINARY) for i in range(n)]

    # At least one celebrity is present at the party.
    model += mip.xsum(c) >= 1

    # A celebrity is a person that everybody at the party knows.
    for i in range(n):
        for j in range(n):
            if j != i and graph[j][i] == 0:
                model += c[i] <= 0

    # A celebrity only knows other celebrities.
    for i in range(n):
        for j in range(n):
            if j != i and graph[i][j] == 1:
                model += c[i] <= c[j]

    return model, {"celebrities": c}
