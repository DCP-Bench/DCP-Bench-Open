# Social golfers: schedule n_groups * group_size golfers over n_weeks weeks, playing in groups
# of group_size each week, so that no two golfers are in the same group more than once.
from exact import Exact


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]  # groups playing each week
    group_size = instance["group_size"]  # golfers in each group
    n_golfers = n_groups * group_size  # every golfer plays once a week

    solver = Exact()

    # assign[g][w] is the group (0..n_groups-1) in which golfer g plays in week w
    assign = [[f"assign_{g}_{w}" for w in range(n_weeks)] for g in range(n_golfers)]
    # plays[g][w][k] = 1 when assign[g][w] == k. Exact has no all-different or counting
    # constraint, so group membership is counted through these 0/1 indicators.
    plays = [[[f"plays_{g}_{w}_{k}" for k in range(n_groups)] for w in range(n_weeks)]
             for g in range(n_golfers)]
    for g in range(n_golfers):
        for w in range(n_weeks):
            solver.addVariable(assign[g][w], 0, n_groups - 1)
            for name in plays[g][w]:
                solver.addVariable(name, 0, 1)
            # each golfer plays in exactly one group every week
            solver.addConstraint([(1, name) for name in plays[g][w]], True, 1, True, 1)
            solver.addConstraint([(k, plays[g][w][k]) for k in range(1, n_groups)] + [(-1, assign[g][w])],
                                 True, 0, True, 0)

    # every group has exactly group_size golfers in every week
    for w in range(n_weeks):
        for k in range(n_groups):
            solver.addConstraint([(1, plays[g][w][k]) for g in range(n_golfers)],
                                 True, group_size, True, group_size)

    # each pair of golfers is in the same group at most once over all weeks. together[w][k] must
    # be 1 when both golfers play in group k in week w (it is only bounded from below, and the
    # solver may keep it 0 otherwise); at most one (week, group) can be counted per pair.
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            together = []
            for w in range(n_weeks):
                for k in range(n_groups):
                    name = f"together_{g1}_{g2}_{w}_{k}"
                    solver.addVariable(name, 0, 1)
                    solver.addConstraint([(1, name), (-1, plays[g1][w][k]), (-1, plays[g2][w][k])],
                                         True, -1)
                    together.append((1, name))
            solver.addConstraint(together, False, 0, True, 1)

    return solver, {"assign": assign}
