# CSPLib 039 rehearsal order. A concert has pieces of different durations, each played by
# a combination of orchestra players. Players arrive immediately before the first piece they
# play and depart immediately after the last one. Devise a rehearsal order that minimises the
# total time players are present but not playing.
import mip


def build(instance):
    n = instance["num_pieces"]
    dur = instance["duration"]
    rehearsal = instance["rehearsal"]
    total = sum(dur)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # before[i][j] = 1 when piece i is rehearsed before piece j (i != j).
    before = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                before[i][j] = model.add_var(f"before_{i}_{j}", var_type=mip.BINARY)

    # the rehearsal order is a total order: exactly one of the two directions for each pair
    for i in range(n):
        for j in range(i + 1, n):
            model += before[i][j] + before[j][i] == 1

    # the pairwise order is transitive (no cycle of three pieces)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if len({i, j, k}) == 3:
                    model += before[i][j] + before[j][k] + before[k][i] <= 2

    # piece i starts after the durations of all pieces rehearsed before it
    start = [mip.xsum(dur[j] * before[j][i] for j in range(n) if j != i) for i in range(n)]

    # slot[i] = number of pieces before piece i. x[i][s] = 1 when piece i is in slot s.
    x = [[model.add_var(f"x_{i}_{s}", var_type=mip.BINARY) for s in range(n)] for i in range(n)]
    for i in range(n):
        model += mip.xsum(x[i][s] for s in range(n)) == 1
        model += mip.xsum(before[j][i] for j in range(n) if j != i) == mip.xsum(s * x[i][s] for s in range(n))
    for s in range(n):
        model += mip.xsum(x[i][s] for i in range(n)) == 1

    # rehearsal_order[s] is the piece rehearsed in slot s
    order = [model.add_var(f"order_{s}", lb=0, ub=n - 1, var_type=mip.INTEGER) for s in range(n)]
    for s in range(n):
        model += order[s] == mip.xsum(i * x[i][s] for i in range(n))

    # each player is present from the start of the first piece they play to the end of the
    # last one; the arrival and departure times are integer, so the objective is integer
    cost_terms = []
    for p in range(len(rehearsal)):
        played = [i for i in range(n) if rehearsal[p][i]]
        if not played:
            continue
        arrive = model.add_var(f"arrive_{p}", lb=0, ub=total, var_type=mip.INTEGER)
        depart = model.add_var(f"depart_{p}", lb=0, ub=total, var_type=mip.INTEGER)
        # the player arrives before every piece they play
        for i in played:
            model += arrive <= start[i]
        # the player stays until the end of every piece they play
        for i in played:
            model += depart >= start[i] + dur[i]
        cost_terms.append(depart - arrive)

    # total waiting time = total presence minus the (constant) total playing time
    model.objective = mip.xsum(cost_terms)

    return model, {"rehearsal_order": order}
