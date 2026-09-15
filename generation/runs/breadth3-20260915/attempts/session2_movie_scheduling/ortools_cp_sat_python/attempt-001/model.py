from ortools.sat.python import cp_model


def build(instance):
    movies = instance["movies"]
    n = len(movies)
    model = cp_model.CpModel()
    selected = [model.new_bool_var(f"s_{i}") for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and movies[i][2] > movies[j][1] and movies[j][2] > movies[i][1]:
                model.add_at_most_one([selected[i], selected[j]])
    model.maximize(sum(selected))
    return model, {"selected_movies": selected}
