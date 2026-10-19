# Social golfers problem (CSPLib 010), cvc5 (pythonic) model, Boolean encoding.
#
# Golfers are n_groups * group_size in number. Each week they are split into
# n_groups groups of group_size golfers each. No two golfers may share a group
# in more than one week.
#
# assign[i][j] is the group number (0-based) of golfer i in week j.
#
# Each golfer sits in exactly one group per week: x[i][j][g] is true when golfer i
# is in group g in week j.

from cvc5.pythonic import Bool, If, Not, And, Or, Sum


def build(instance):
    group_size = instance["group_size"]
    n_groups = instance["n_groups"]
    n_weeks = instance["n_weeks"]
    n_golfers = n_groups * group_size

    x = [[[Bool(f"x_{i}_{j}_{g}") for g in range(n_groups)] for j in range(n_weeks)]
         for i in range(n_golfers)]

    constraints = []

    # Each golfer plays in exactly one group every week.
    for i in range(n_golfers):
        for j in range(n_weeks):
            constraints.append(Or([x[i][j][g] for g in range(n_groups)]))
            for g in range(n_groups):
                for h in range(g + 1, n_groups):
                    constraints.append(Or(Not(x[i][j][g]), Not(x[i][j][h])))

    # Each week, every group holds exactly group_size golfers.
    for j in range(n_weeks):
        for g in range(n_groups):
            constraints.append(
                Sum([If(x[i][j][g], 1, 0) for i in range(n_golfers)]) == group_size
            )

    # No golfer plays in the same group as any other golfer on more than one
    # occasion: two golfers who share a group in week j1 and in week j2 are forbidden.
    for i in range(n_golfers):
        for k in range(i + 1, n_golfers):
            for g in range(n_groups):
                for j1 in range(n_weeks):
                    for j2 in range(j1 + 1, n_weeks):
                        constraints.append(
                            Not(And(x[i][j1][g], x[k][j1][g], x[i][j2][g], x[k][j2][g]))
                        )

    # Declared output: the group number of each golfer in each week.
    assign = [[Sum([If(x[i][j][g], g, 0) for g in range(n_groups)]) for j in range(n_weeks)]
              for i in range(n_golfers)]

    return constraints, {"assign": assign}
