# Finding celebrities: a celebrity is a guest whom everybody at the party knows and who
# knows only celebrities. Decide, from the "who knows whom" table, who the celebrities are.
from pychoco.model import Model


def build(instance):
    graph = instance["graph"]  # graph[i][j] = 1 if guest i knows guest j
    n = len(graph)

    model = Model()

    # celebrities[i] = 1 if guest i is a celebrity
    celebrities = [model.boolvar(name=f"celebrities_{i}") for i in range(n)]
    # number of celebrities (at least one is present at the party)
    num_celebrities = model.intvar(1, n, name="num_celebrities")
    model.sum(celebrities, "=", num_celebrities).post()

    # A guest is a celebrity exactly when everybody knows them and they know exactly
    # as many people as there are celebrities (so they know only celebrities, as
    # everybody knows every celebrity).
    for i in range(n):
        known_by_everybody = sum(graph[j][i] for j in range(n)) == n
        people_known = sum(graph[i])
        if known_by_everybody:
            model.arithm(num_celebrities, "=", people_known).reify_with(celebrities[i])
        else:
            model.arithm(celebrities[i], "=", 0).post()

    return model, {"celebrities": celebrities}
