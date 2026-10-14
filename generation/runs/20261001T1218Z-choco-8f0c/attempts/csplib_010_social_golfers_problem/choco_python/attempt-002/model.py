# Social golfers: schedule golfers into groups week by week so that no two
# golfers play in the same group more than once.
from pychoco.model import Model


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]  # groups playing in each week
    group_size = instance["group_size"]  # golfers in each group
    n_golfers = n_groups * group_size  # every golfer plays once a week

    model = Model()

    # assign[g][w] = the group in which golfer g plays in week w
    assign = [[model.intvar(0, n_groups - 1, name=f"assign_{g}_{w}") for w in range(n_weeks)]
              for g in range(n_golfers)]

    # each group has exactly group_size players in every week
    for w in range(n_weeks):
        model.global_cardinality([assign[g][w] for g in range(n_golfers)], list(range(n_groups)),
                                 [model.intvar(group_size, group_size) for _ in range(n_groups)]).post()

    # Each pair of golfers meets (is in the same group) in at most one week.
    # Two golfers meet in both of weeks w1 and w2 exactly when they are in the same
    # group in w1 and also in the same group in w2, i.e. when the pair
    # (group in w1, group in w2) is the same for both. So the constraint is: for every
    # two weeks, the pairs (group in w1, group in w2) of all golfers are different from
    # each other. The pair is coded as one number, n_groups * group_in_w1 + group_in_w2,
    # and these codes must be all different.
    for w1 in range(n_weeks):
        for w2 in range(w1 + 1, n_weeks):
            codes = []
            for g in range(n_golfers):
                code = model.intvar(0, n_groups * n_groups - 1, name=f"code_{g}_{w1}_{w2}")
                model.scalar([assign[g][w1], assign[g][w2]], [n_groups, 1], "=", code).post()
                codes.append(code)
            model.all_different(codes).post()

    return model, {"assign": assign}
