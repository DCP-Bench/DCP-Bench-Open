# Movie scheduling: accept as many movie jobs as possible when each job occupies a period of days
# and two jobs whose periods overlap cannot both be accepted.
from exact import Exact


def build(instance):
    movies = instance["movies"]  # each movie is [title, first day of filming, last day of filming]
    num_movies = len(movies)

    solver = Exact()

    # selected_movies[i] = 1 if movie i is accepted
    selected_movies = [f"selected_{i}" for i in range(num_movies)]
    for name in selected_movies:
        solver.addVariable(name, 0, 1)

    # accepted movies must not overlap: two movies conflict when each ends on or after the day the
    # other starts, and then at most one of them can be selected
    for i in range(num_movies):
        for j in range(i + 1, num_movies):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                solver.addConstraint([(1, selected_movies[i]), (1, selected_movies[j])],
                                     False, 0, True, 1)

    # maximise the number of accepted movies
    return (solver, {"selected_movies": selected_movies},
            ("maximize", [(1, name) for name in selected_movies]))
