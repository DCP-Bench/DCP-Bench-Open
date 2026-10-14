"""Social golfers: schedule the golfers of a club into groups, week after week,
so that no two golfers play in the same group on more than one occasion.

There are n_groups * group_size golfers. Every week each golfer plays in one
group, and every group has exactly group_size players.
"""
import pulp


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size

    golfers, weeks, groups = range(n_golfers), range(n_weeks), range(n_groups)

    problem = pulp.LpProblem("social_golfers", pulp.LpMinimize)

    # plays[g][w][k] = 1 if golfer g plays in group k in week w
    plays = [[[pulp.LpVariable(f"plays_{g}_{w}_{k}", cat="Binary") for k in groups]
              for w in weeks] for g in golfers]

    # assign[g][w] = the group of golfer g in week w (declared output), a bounded
    # integer tied to the 0/1 variables by equality; 0..n_groups-1 is the group
    # numbering of the problem.
    assign = [[pulp.LpVariable(f"assign_{g}_{w}", 0, n_groups - 1, cat="Integer")
               for w in weeks] for g in golfers]

    # every golfer plays in exactly one group each week
    for g in golfers:
        for w in weeks:
            problem += pulp.lpSum(plays[g][w]) == 1
            problem += assign[g][w] == pulp.lpSum(k * plays[g][w][k] for k in groups)

    # each group has exactly group_size players, every week
    for w in weeks:
        for k in groups:
            problem += pulp.lpSum(plays[g][w][k] for g in golfers) == group_size

    # each pair of golfers meets at most once: together[w] is forced to 1 when both
    # golfers play in the same group in week w, and at most one week may have it.
    # One row per group suffices because a golfer plays in exactly one group.
    for g1 in golfers:
        for g2 in range(g1 + 1, n_golfers):
            together = [pulp.LpVariable(f"together_{g1}_{g2}_{w}", 0, 1) for w in weeks]
            for w in weeks:
                for k in groups:
                    problem += together[w] >= plays[g1][w][k] + plays[g2][w][k] - 1
            problem += pulp.lpSum(together) <= 1

    return problem, {"assign": assign}
