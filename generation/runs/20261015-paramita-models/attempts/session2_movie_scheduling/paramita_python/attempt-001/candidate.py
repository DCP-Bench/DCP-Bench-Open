"""Interval scheduling: pick the largest set of movies whose filming periods do not overlap.

Each movie i has a Bool s_i: true when the actor accepts movie i.
Each movie is an entry [title, first day, last day] in the input order.
"""

from paramita.modelling import Bool


def build(instance):
    movies = instance["movies"]  # movies[i] = [title, first day, last day]
    m = len(movies)

    s = [Bool(f"s_{i}") for i in range(m)]  # s[i]: movie i is selected

    starts = [movie[1] for movie in movies]
    ends = [movie[2] for movie in movies]

    cons = []

    # cannot simultaneously accept two jobs whose intervals overlap:
    # two filming periods overlap when they share a day, i.e. start_i <= end_j and start_j <= end_i
    for i in range(m):
        for j in range(i + 1, m):
            if starts[i] <= ends[j] and starts[j] <= ends[i]:
                cons.append(~(s[i] & s[j]))

    # largest possible set of jobs: maximise the number of selected movies
    total = sum(s)

    return cons, {"selected_movies": s}, ("maximize", total)
