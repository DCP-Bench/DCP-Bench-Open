# Movie scheduling: an actor has offers for several movies, each filmed over a first and
# last day and all paying the same fee. Accept the largest set of movies such that no
# two of them have overlapping filming periods.
from pychoco.model import Model


def build(instance):
    movies = instance["movies"]  # each movie is [title, first day, last day]
    num_movies = len(movies)

    model = Model()

    # selected_movies[i] is true when movie i is accepted
    selected_movies = [model.boolvar(name=f"selected_{i}") for i in range(num_movies)]

    # two movies whose filming periods share a day cannot both be accepted
    for i in range(num_movies):
        for j in range(i + 1, num_movies):
            if movies[i][2] >= movies[j][1] and movies[j][2] >= movies[i][1]:
                model.sum([selected_movies[i], selected_movies[j]], "<=", 1).post()

    # number of accepted movies (Choco maximises one variable, so it gets its own)
    num_selected_movies = model.intvar(0, num_movies, name="num_selected_movies")
    model.sum(selected_movies, "=", num_selected_movies).post()

    return model, {"selected_movies": selected_movies}, ("maximize", num_selected_movies)
