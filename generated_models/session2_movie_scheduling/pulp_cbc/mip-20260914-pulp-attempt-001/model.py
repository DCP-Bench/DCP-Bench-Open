import pulp


def build(instance):
    movies = instance["movies"]
    indices = range(len(movies))
    problem = pulp.LpProblem("movie_scheduling", pulp.LpMaximize)
    selected = [pulp.LpVariable(f"select_{i}", cat="Binary") for i in indices]
    for i in indices:
        for j in indices:
            if i != j and movies[i][2] > movies[j][1] and movies[j][2] > movies[i][1]:
                problem += selected[i] + selected[j] <= 1
    problem += pulp.lpSum(selected)
    return problem, {"selected_movies": selected}
