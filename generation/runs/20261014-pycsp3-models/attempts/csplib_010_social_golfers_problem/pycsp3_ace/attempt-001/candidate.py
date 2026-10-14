from pycsp3 import *

# Social golfers: golfers play once a week in groups of a fixed size, and no two
# golfers may share a group on more than one occasion.
n_groups = data.n_groups
group_size = data.group_size
n_weeks = data.n_weeks
n_golfers = n_groups * group_size

# every pair of golfers
pairs = [(i, k) for i in range(n_golfers) for k in range(i + 1, n_golfers)]

# assign[i][j] is the group of golfer i in week j
assign = VarArray(size=[n_golfers, n_weeks], dom=range(n_groups))

# meet[p][j] is 1 when the golfers of pair p are in the same group in week j
meet = VarArray(size=[len(pairs), n_weeks], dom={0, 1})

satisfy(
    # each week the golfers are split into groups of the given size
    [Count([assign[i][j] for i in range(n_golfers)], value=g) == group_size
     for j in range(n_weeks) for g in range(n_groups)],
    # the meet flag records whether two golfers share a group in a week
    [(meet[p][j] == 1) == (assign[i][j] == assign[k][j])
     for p, (i, k) in enumerate(pairs) for j in range(n_weeks)],
    # no two golfers play in the same group on more than one occasion
    [Sum(meet[p][j] for j in range(n_weeks)) <= 1 for p in range(len(pairs))],
)
