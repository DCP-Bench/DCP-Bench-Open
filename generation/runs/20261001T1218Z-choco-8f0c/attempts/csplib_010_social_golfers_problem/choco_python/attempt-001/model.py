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
    # (pychoco's count takes the number of occurrences as a variable)
    for w in range(n_weeks):
        week = [assign[g][w] for g in range(n_golfers)]
        for group in range(n_groups):
            model.count(group, week, model.intvar(group_size, group_size)).post()

    # each pair of golfers meets (is in the same group) in at most one week
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            meets = [model.arithm(assign[g1][w], "=", assign[g2][w]).reify() for w in range(n_weeks)]
            model.sum(meets, "<=", 1).post()

    return model, {"assign": assign}
