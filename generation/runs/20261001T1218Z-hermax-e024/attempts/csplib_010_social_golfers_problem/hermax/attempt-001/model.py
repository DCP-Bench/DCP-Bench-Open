# Social golfers: schedule golfers into groups of equal size for several
# weeks so that no two golfers play in the same group more than once.
from hermax.model import Model


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]  # groups playing each week
    group_size = instance["group_size"]  # golfers in each group
    n_golfers = n_groups * group_size  # every golfer plays once a week

    m = Model()
    # assign[g][w] = the group (numbered from 0) golfer g plays in during week w
    assign = m.int_matrix("assign", n_golfers, n_weeks, 0, n_groups - 1)

    # every group has exactly group_size golfers in every week
    for w in range(n_weeks):
        for group in range(n_groups):
            m &= (sum((assign[g][w] == group) for g in range(n_golfers)) == group_size)

    # any two golfers are in the same group in at most one week. meet[w] is
    # forced true when the pair shares a group in week w (forcing one way is
    # enough because it is only ever bounded from above), and at most one week
    # per pair may have it true.
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            meet = m.bool_vector(f"meet_{g1}_{g2}", n_weeks)
            for w in range(n_weeks):
                for group in range(n_groups):
                    m &= (~(assign[g1][w] == group) | ~(assign[g2][w] == group) | meet[w])
            m &= meet.at_most_one()

    return m, {"assign": assign}
