"""Social golfers problem.

A golf club has n_groups * group_size golfers. Each week they play in n_groups
groups of group_size golfers. No two golfers may share a group on more than one
occasion. Output assign[i][j], the 0-based group of golfer i in week j.

Encoding: one-hot per golfer, week and group: p[i][j][g] is true when golfer i
plays in group g in week j.
"""

from paramita.modelling import Bool, If


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size

    p = [[[Bool(f"p_{i}_{j}_{g}") for g in range(n_groups)]
          for j in range(n_weeks)] for i in range(n_golfers)]

    cons = []

    # Each golfer plays in exactly one group each week.
    for i in range(n_golfers):
        for j in range(n_weeks):
            cons.append(sum(p[i][j]) == 1)

    # Each group in each week holds exactly group_size golfers.
    for j in range(n_weeks):
        for g in range(n_groups):
            cons.append(sum(p[i][j][g] for i in range(n_golfers)) == group_size)

    # Symmetry breaking: the golfers of week 0 are interchangeable, so number
    # them so that golfer i plays in group i // group_size in week 0.
    for i in range(n_golfers):
        cons.append(p[i][0][i // group_size])

    # No two golfers meet more than once. meet[a][b][j] is forced true when
    # golfers a and b share a group in week j, and each pair may have at most
    # one such week.
    for a in range(n_golfers):
        for b in range(a + 1, n_golfers):
            meets = []
            for j in range(n_weeks):
                meet = Bool(f"meet_{a}_{b}_{j}")
                meets.append(meet)
                for g in range(n_groups):
                    cons.append(~p[a][j][g] | ~p[b][j][g] | meet)
            cons.append(sum(meets) <= 1)

    assign = [[sum(g * p[i][j][g] for g in range(n_groups)) for j in range(n_weeks)]
              for i in range(n_golfers)]

    return cons, {"assign": assign}
