import cpmpy as cp


def build(instance):
    movies = instance["movies"]
    n = len(movies)
    selected = cp.boolvar(shape=n, name="selected_movies")
    model = cp.Model()
    # Each row is a title with a start and an end; two that overlap cannot both go.
    for i in range(n):
        for j in range(n):
            if i != j and movies[i][2] > movies[j][1] and movies[j][2] > movies[i][1]:
                model += selected[i] + selected[j] <= 1
    model.maximize(cp.sum([selected[i] for i in range(n)]))
    return model, {"selected_movies": [selected[i] for i in range(n)]}
