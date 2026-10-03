# Movie scheduling: an actor is offered several movies, each filmed over a first and
# a last day. Two movies whose filming days overlap cannot both be taken. Take the
# largest possible number of movies.
from hermax.model import Model


def build(instance):
    movies = instance["movies"]  # movies[i] = [title, first day, last day] of movie i
    n = len(movies)

    m = Model()
    # selected_movies[i] = movie i is taken
    selected_movies = m.bool_vector("selected_movies", n)

    # Two different movies whose filming periods share a day (each ends on or after
    # the day the other starts) cannot both be selected.
    for i in range(n):
        for j in range(i + 1, n):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                m &= (~selected_movies[i] | ~selected_movies[j])

    # Maximise the number of movies taken. A soft clause pays when its literal is
    # false, so every movie that is not selected pays 1; the least paid is the most taken.
    for i in range(n):
        m.obj[1] += selected_movies[i]

    return m, {"selected_movies": selected_movies}
