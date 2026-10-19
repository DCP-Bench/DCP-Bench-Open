# Social golfers problem (CSPLib 010), cvc5 (pythonic) model.
#
# Golfers are n_groups * group_size in number. Each week they are split into
# n_groups groups of group_size golfers each. No two golfers may share a group
# in more than one week.
#
# assign[i][j] is the group number (0-based) of golfer i in week j.

from cvc5.pythonic import Int, If, Sum


def build(instance):
    group_size = instance["group_size"]
    n_groups = instance["n_groups"]
    n_weeks = instance["n_weeks"]
    n_golfers = n_groups * group_size

    assign = [[Int(f"a_{i}_{j}") for j in range(n_weeks)] for i in range(n_golfers)]

    constraints = []

    # Each golfer's group is a valid group number in every week.
    for i in range(n_golfers):
        for j in range(n_weeks):
            constraints.append(assign[i][j] >= 0)
            constraints.append(assign[i][j] <= n_groups - 1)

    # Each week, every group holds exactly group_size golfers.
    for j in range(n_weeks):
        for g in range(n_groups):
            constraints.append(
                Sum([If(assign[i][j] == g, 1, 0) for i in range(n_golfers)]) == group_size
            )

    # No two golfers play in the same group in more than one week.
    for i in range(n_golfers):
        for k in range(i + 1, n_golfers):
            constraints.append(
                Sum([If(assign[i][j] == assign[k][j], 1, 0) for j in range(n_weeks)]) <= 1
            )

    return constraints, {"assign": assign}
