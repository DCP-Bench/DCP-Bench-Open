import z3


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size

    assign = [[z3.Int(f"assign_{g}_{w}") for w in range(n_weeks)] for g in range(n_golfers)]
    constraints = []
    for row in assign:
        for cell in row:
            constraints.append(z3.And(cell >= 0, cell <= n_groups - 1))
    # Each group holds exactly group_size players every week.
    for group in range(n_groups):
        for week in range(n_weeks):
            members = [z3.If(assign[g][week] == group, 1, 0) for g in range(n_golfers)]
            constraints.append(z3.Sum(members) == group_size)
    # Any two players share a group at most once over the season.
    for first in range(n_golfers):
        for second in range(first + 1, n_golfers):
            together = [z3.If(assign[first][week] == assign[second][week], 1, 0)
                        for week in range(n_weeks)]
            constraints.append(z3.Sum(together) <= 1)
    return constraints, {"assign": assign}
