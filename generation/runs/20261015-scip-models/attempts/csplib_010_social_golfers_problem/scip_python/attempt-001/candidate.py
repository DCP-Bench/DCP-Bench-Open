# Social golfers: schedule n_groups * group_size golfers into n_groups groups of
# size group_size for n_weeks weeks, so that no two golfers share a group more
# than once.
from pyscipopt import Model, quicksum


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size
    m = Model()

    # play[p, w, k] = 1 if golfer p is in group k in week w
    play = {
        (p, w, k): m.addVar(name=f"play_{p}_{w}_{k}", vtype="B")
        for p in range(n_golfers)
        for w in range(n_weeks)
        for k in range(n_groups)
    }

    # each golfer plays in exactly one group each week
    for p in range(n_golfers):
        for w in range(n_weeks):
            # each golfer plays in exactly one group per week
            m.addCons(quicksum(play[p, w, k] for k in range(n_groups)) == 1)

    # each group has exactly group_size golfers each week
    for w in range(n_weeks):
        for k in range(n_groups):
            # every group holds group_size golfers
            m.addCons(quicksum(play[p, w, k] for p in range(n_golfers)) == group_size)

    # no two golfers play together more than once: together[p, q, w, k] is 1
    # only if golfers p and q are both in group k in week w (it is forced to 1
    # by the lower bound, and an unused 1 only tightens the count below)
    for p in range(n_golfers):
        for q in range(p + 1, n_golfers):
            together = []
            for w in range(n_weeks):
                for k in range(n_groups):
                    t = m.addVar(name=f"together_{p}_{q}_{w}_{k}", vtype="B")
                    m.addCons(t >= play[p, w, k] + play[q, w, k] - 1)
                    together.append(t)
            # golfers p and q meet at most once over all weeks
            m.addCons(quicksum(together) <= 1)

    # the output gives the group of each golfer in each week
    assign = [
        [quicksum(k * play[p, w, k] for k in range(n_groups)) for w in range(n_weeks)]
        for p in range(n_golfers)
    ]
    return m, {"assign": assign}
