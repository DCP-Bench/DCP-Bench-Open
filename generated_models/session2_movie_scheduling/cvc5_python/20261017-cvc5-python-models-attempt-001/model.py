# Movie scheduling: an actor accepts a set of film offers, each with a first and
# last day of filming. Accepted films may not overlap. Maximise the number of
# accepted films. Output selected_movies[i] is true when film i is accepted.
# Each movie is an instance row [name, first_day, last_day]; the name is ignored.
import cvc5.pythonic as cz


def build(instance):
    movies = instance["movies"]
    n = len(movies)
    starts = [int(m[1]) for m in movies]
    ends = [int(m[2]) for m in movies]

    selected = list(cz.Bools([f"sel{i}" for i in range(n)]))

    constraints = []

    # you cannot simultaneously accept two jobs whose intervals overlap.
    for i in range(n):
        for j in range(i + 1, n):
            if starts[i] <= ends[j] and starts[j] <= ends[i]:
                constraints.append(cz.Or(cz.Not(selected[i]), cz.Not(selected[j])))

    # you seek the largest possible set of jobs (intervals) such that no two of them conflict.
    objective = cz.Sum([cz.If(b, 1, 0) for b in selected]) if n > 0 else 0

    outputs = {"selected_movies": selected}
    return constraints, outputs, ("maximize", objective)
