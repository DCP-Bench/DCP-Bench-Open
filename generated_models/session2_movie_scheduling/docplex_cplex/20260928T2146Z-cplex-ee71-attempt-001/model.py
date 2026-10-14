"""Movie scheduling: accept as many film offers as possible without two filming periods overlapping."""
from docplex.mp.model import Model


def build(instance):
    movies = instance["movies"]  # each is [title, first day, last day]
    n = len(movies)

    model = Model("movie_scheduling")

    # selected[i] is 1 when offer i is accepted.
    selected = model.binary_var_list(n, name="selected_movies")

    # Two films whose filming periods overlap, sharing even one day, cannot both be accepted.
    for i in range(n):
        for j in range(i + 1, n):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                model.add_constraint(selected[i] + selected[j] <= 1, ctname=f"overlap_{i}_{j}")

    # Maximise the number of films accepted.
    model.maximize(model.sum(selected))

    return model, {"selected_movies": selected}
