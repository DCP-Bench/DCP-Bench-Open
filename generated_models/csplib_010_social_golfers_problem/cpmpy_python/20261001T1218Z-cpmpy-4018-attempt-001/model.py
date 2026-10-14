# Social golfers: golfers play once a week in groups of a fixed size. Find a
# schedule over n_weeks weeks in which every group is full and no two golfers
# play in the same group more than once.
import cpmpy as cp


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size  # every golfer plays every week, so the field fills all groups

    # assign[g, w] = the group golfer g plays in during week w
    assign = cp.intvar(0, n_groups - 1, shape=(n_golfers, n_weeks), name="assign")

    model = cp.Model()

    # Each group has exactly group_size players in every week.
    for w in range(n_weeks):
        for k in range(n_groups):
            model += cp.sum(assign[:, w] == k) == group_size

    # Two golfers share a group in at most one week.
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            model += cp.sum(assign[g1, :] == assign[g2, :]) <= 1

    return model, {"assign": assign}
