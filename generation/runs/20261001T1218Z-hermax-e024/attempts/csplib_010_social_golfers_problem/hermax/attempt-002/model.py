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
    # in_group[g][w][k] = golfer g plays in group k during week w. The same
    # choice as `assign`, in the one-hot form that the counting below uses.
    in_group = [[m.bool_vector(f"in_{g}_{w}", n_groups) for w in range(n_weeks)]
                for g in range(n_golfers)]
    for g in range(n_golfers):
        for w in range(n_weeks):
            m &= in_group[g][w].exactly_one()
            for k in range(n_groups):
                m &= (~in_group[g][w][k] | (assign[g][w] == k))
                m &= (in_group[g][w][k] | ~(assign[g][w] == k))

    # every group has exactly group_size golfers in every week
    for w in range(n_weeks):
        for k in range(n_groups):
            m &= (sum(in_group[g][w][k] for g in range(n_golfers)) == group_size)

    # meet[g1][g2][w] says golfers g1 < g2 share a group in week w. It is posted
    # as an equivalence, so that the counts below are exact.
    meet = {}
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            flags = m.bool_vector(f"meet_{g1}_{g2}", n_weeks)
            for w in range(n_weeks):
                for k in range(n_groups):
                    # both in group k -> they meet
                    m &= (~in_group[g1][w][k] | ~in_group[g2][w][k] | flags[w])
                    # they meet and g1 is in group k -> g2 is in group k too
                    m &= (~flags[w] | ~in_group[g1][w][k] | in_group[g2][w][k])
                meet[(g1, g2, w)] = flags[w]
            # any two golfers are in the same group in at most one week
            m &= flags.at_most_one()

    # In any week a golfer plays with exactly group_size - 1 others. This follows
    # from the group sizes; it is stated again on the meeting flags because it
    # gives the solver a strong count to propagate on them.
    for g in range(n_golfers):
        for w in range(n_weeks):
            partners = [meet[(min(g, h), max(g, h), w)] for h in range(n_golfers) if h != g]
            m &= (sum(partners) == group_size - 1)

    return m, {"assign": assign}
