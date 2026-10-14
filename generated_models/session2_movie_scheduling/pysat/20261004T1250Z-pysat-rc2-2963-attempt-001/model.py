# Movie scheduling: an actor accepts as many film offers as possible, where
# each film needs the actor from its first to its last day of filming and
# no two accepted films may overlap.
from pysat.formula import IDPool, WCNF


def build(instance):
    movies = instance["movies"]  # rows of [title, first day, last day]
    n = len(movies)

    pool = IDPool()
    # selected_movies[i] is true when film i is accepted.
    selected = [pool.id(("selected", i)) for i in range(n)]

    formula = WCNF()
    # Two films whose filming periods overlap (each ends on or after the day
    # the other starts) cannot both be accepted.
    for i in range(n):
        for j in range(i + 1, n):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                formula.append([-selected[i], -selected[j]])

    # Maximise the number of accepted films: every film turned down pays 1,
    # so the cost is the shortfall from n.
    for i in range(n):
        formula.append([selected[i]], weight=1)

    return formula, {"selected_movies": selected}
