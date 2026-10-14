"""Movie scheduling: accept as many film offers as possible without two filming periods overlapping."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    movies = instance["movies"]  # each is [title, first day, last day]
    films = range(len(movies))

    model = gp.Model("movie_scheduling")

    # selected_movies[i] is 1 when offer i is accepted.
    selected = model.addVars(films, vtype=GRB.BINARY, name="selected_movies")

    # Two films whose filming periods overlap, sharing even one day, cannot both be accepted.
    for i in films:
        for j in range(i + 1, len(movies)):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                model.addConstr(selected[i] + selected[j] <= 1, name=f"overlap[{i},{j}]")

    # Maximise the number of films accepted.
    model.setObjective(selected.sum(), GRB.MAXIMIZE)

    return model, {"selected_movies": [selected[i] for i in films]}
