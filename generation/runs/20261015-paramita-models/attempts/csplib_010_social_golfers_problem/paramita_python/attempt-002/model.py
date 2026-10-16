"""Social golfers problem.

A golf club has n_groups * group_size golfers. Each week they play in n_groups
groups of group_size golfers. No two golfers may share a group on more than one
occasion. Output assign[i][j], the 0-based group of golfer i in week j.

Encoding: one-hot per golfer, week and group: p[i][j][g] is true when golfer i
plays in group g in week j. Meeting Bools meet[a][b][j] record that golfers a
and b share a group in week j, in both directions, so that the counts below are
exact.
"""

from paramita.modelling import Bool


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

    # meet[a][b][j] (a < b) is the meeting of golfers a and b in week j.
    meet = {}
    for a in range(n_golfers):
        for b in range(a + 1, n_golfers):
            for j in range(n_weeks):
                m = Bool(f"meet_{a}_{b}_{j}")
                meet[a, b, j] = m
                meet[b, a, j] = m
                for g in range(n_groups):
                    # Golfers in the same group in week j meet in week j.
                    cons.append(~p[a][j][g] | ~p[b][j][g] | m)
                    # A meeting means they share a group in week j.
                    cons.append(~m | ~p[a][j][g] | p[b][j][g])

    # No two golfers meet more than once.
    for a in range(n_golfers):
        for b in range(a + 1, n_golfers):
            cons.append(sum(meet[a, b, j] for j in range(n_weeks)) <= 1)

    # Each golfer meets exactly group_size - 1 others each week.
    for a in range(n_golfers):
        for j in range(n_weeks):
            cons.append(sum(meet[a, b, j] for b in range(n_golfers) if b != a)
                        == group_size - 1)

    assign = [[sum(g * p[i][j][g] for g in range(n_groups)) for j in range(n_weeks)]
              for i in range(n_golfers)]

    return cons, {"assign": assign}
