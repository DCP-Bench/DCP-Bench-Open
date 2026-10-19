# Social golfers problem (CSPLib 010), cvc5 (pythonic) model, Boolean encoding.
#
# Golfers are n_groups * group_size in number. Each week they are split into
# n_groups groups of group_size golfers each. No golfer may play in the same
# group as another golfer on more than one occasion.
#
# assign[i][j] is the group number (0-based) of golfer i in week j.
#
# x[i][j][g] is true when golfer i is in group g in week j. Every constraint is
# a clause over these Booleans and meet Booleans m[i][k][j] (golfers i and k share
# a group in week j), so the solver works on propositional structure.

from cvc5.pythonic import If, Not, Or, Bool, Sum, SolverFor


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

    # Meet Booleans: m[i][k][j] is forced true when golfers i and k share a group
    # in week j.
    m = {}
    for i in range(n_golfers):
        for k in range(i + 1, n_golfers):
            for j in range(n_weeks):
                m[(i, k, j)] = Bool(f"m_{i}_{k}_{j}")
                for g in range(n_groups):
                    constraints.append(
                        Or(Not(x[i][j][g]), Not(x[k][j][g]), m[(i, k, j)])
                    )

    # No two golfers play in the same group as each other on more than one
    # occasion: for each pair, at most one week in which they meet.
    for i in range(n_golfers):
        for k in range(i + 1, n_golfers):
            for j1 in range(n_weeks):
                for j2 in range(j1 + 1, n_weeks):
                    constraints.append(
                        Or(Not(m[(i, k, j1)]), Not(m[(i, k, j2)]))
                    )

    # Declared output: the group number of each golfer in each week.
    assign = [[Sum([If(x[i][j][g], g, 0) for g in range(n_groups)])
               for j in range(n_weeks)]
              for i in range(n_golfers)]

    s = SolverFor("QF_LIA")
    s.add(*constraints)
    return s, {"assign": assign}
