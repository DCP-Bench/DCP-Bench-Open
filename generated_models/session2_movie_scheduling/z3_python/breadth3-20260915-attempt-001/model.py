import z3


def build(instance):
    movies = instance["movies"]
    n = len(movies)
    selected = [z3.Bool(f"s_{i}") for i in range(n)]
    picked = [z3.If(selected[i], 1, 0) for i in range(n)]
    constraints = []
    for i in range(n):
        for j in range(n):
            if i != j and movies[i][2] > movies[j][1] and movies[j][2] > movies[i][1]:
                constraints.append(z3.Not(z3.And(selected[i], selected[j])))
    return constraints, {"selected_movies": selected}, ("maximize", z3.Sum(picked))
