# Movie scheduling: choose the largest set of films whose filming periods do not overlap,
# so that the actor is free for every film they accept.
from pyscipopt import Model, quicksum


def build(instance):
    movies = instance["movies"]  # rows of [title, first filming day, last filming day]
    n = len(movies)
    start = [int(mv[1]) for mv in movies]
    end = [int(mv[2]) for mv in movies]

    m = Model()
    # selected[i] = 1 if the actor accepts film i
    selected = [m.addVar(name=f"selected{i + 1}", vtype="B") for i in range(n)]

    # no two accepted films may overlap: their filming periods share a day
    # (periods are inclusive; the data has no touching endpoints, so this matches either reading)
    for i in range(n):
        for j in range(i + 1, n):
            if start[i] <= end[j] and start[j] <= end[i]:
                m.addCons(selected[i] + selected[j] <= 1)

    # maximise the number of accepted films (every film pays the same fee)
    m.setObjective(quicksum(selected), "maximize")

    return m, {"selected_movies": selected}
