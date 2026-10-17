# Movie scheduling: accept the largest set of movie offers such that no two accepted
# movies have overlapping filming intervals. Each movie is [name, first_day, last_day].
# Output selected_movies[i] is 1 when movie i is accepted, in input order.
import mip


def build(instance):
    movies = instance["movies"]
    n = len(movies)
    starts = [m[1] for m in movies]
    ends = [m[2] for m in movies]

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
    x = [model.add_var(f"select_{i}", var_type=mip.BINARY) for i in range(n)]

    # you cannot simultaneously accept two jobs whose intervals overlap.
    # Intervals are whole days, so two intervals overlap exactly when they share a day.
    # One row per day forbids every overlapping pair at once.
    if n > 0:
        for day in range(min(starts), max(ends) + 1):
            members = [x[i] for i in range(n) if starts[i] <= day <= ends[i]]
            if len(members) >= 2:
                model.add_constr(mip.xsum(members) <= 1)

    # you seek the largest possible set of jobs (intervals) such that no two of them conflict
    model.objective = mip.xsum(x)

    return model, {"selected_movies": x}
