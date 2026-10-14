"""Social golfers: schedule golfers into groups, week by week, so that no two golfers
play in the same group more than once.

There are n_groups groups of group_size golfers each, and every golfer plays once a week.
assign[i][w] is the group of golfer i in week w.
"""
from docplex.mp.model import Model


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]

    n_golfers = n_groups * group_size
    golfers = range(n_golfers)
    groups = range(n_groups)

    model = Model("social_golfers")
    # The "no two golfers share a group twice" rule is a quadratic constraint over binaries,
    # which is not convex. CPLEX refuses such a constraint unless it is told to search for a
    # global optimum.
    model.parameters.optimalitytarget = 3

    # Symmetry breaking: week 0 is fixed. Golfers 0..group_size-1 play in group 0, the next
    # group_size golfers in group 1, and so on. Renaming the golfers turns any schedule into
    # one with this first week, and renaming golfers keeps every pair of golfers that meets
    # twice meeting twice, so every schedule has a renamed copy in this model.
    # in_group[i, w, k] is 1 when golfer i plays in group k in week w, for the weeks after
    # the first.
    in_group = {(i, w, k): model.binary_var(name=f"in_group_{i}_{w}_{k}")
                for i in golfers for w in range(1, n_weeks) for k in groups}

    def plays(i, w, k):
        """1 if golfer i plays in group k in week w, as a number or a variable."""
        if w == 0:
            return 1 if k == i // group_size else 0
        return in_group[i, w, k]

    for w in range(1, n_weeks):
        # Every golfer plays in exactly one group.
        for i in golfers:
            model.add_constraint(model.sum(in_group[i, w, k] for k in groups) == 1)
        # Each group has exactly group_size golfers.
        for k in groups:
            model.add_constraint(model.sum(in_group[i, w, k] for i in golfers) == group_size)

    # Each pair of golfers plays together in at most one week. The meetings of a pair are the
    # (week, group) cells where both are in the group; week 0 is a known number.
    for i in golfers:
        for j in range(i + 1, n_golfers):
            met_in_week_0 = 1 if i // group_size == j // group_size else 0
            meetings = model.sum(plays(i, w, k) * plays(j, w, k)
                                 for w in range(1, n_weeks) for k in groups)
            model.add_constraint(meetings <= 1 - met_in_week_0)

    # The declared output: the group number of each golfer in each week.
    assign = [[model.sum(k * in_group[i, w, k] for k in groups) if w > 0 else i // group_size
               for w in range(n_weeks)] for i in golfers]
    return model, {"assign": assign}
