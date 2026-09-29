# Social golfers: golfers play once a week in groups of a fixed size. Find a
# schedule over n_weeks weeks in which every group is full and no two golfers
# play in the same group more than once.
from ortools.sat.python import cp_model


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size

    model = cp_model.CpModel()

    # assign[g][w] = the group golfer g plays in during week w
    assign = [[model.new_int_var(0, n_groups - 1, f"assign_{g}_{w}") for w in range(n_weeks)] for g in range(n_golfers)]
    # in_group[g][w][k] is true when golfer g plays in group k in week w
    in_group = [[[model.new_bool_var(f"in_{g}_{w}_{k}") for k in range(n_groups)] for w in range(n_weeks)]
                for g in range(n_golfers)]
    for g in range(n_golfers):
        for w in range(n_weeks):
            model.add_exactly_one(in_group[g][w])
            model.add(assign[g][w] == sum(k * in_group[g][w][k] for k in range(n_groups)))

    # C1: every group has exactly group_size players in every week
    for w in range(n_weeks):
        for k in range(n_groups):
            model.add(sum(in_group[g][w][k] for g in range(n_golfers)) == group_size)

    # C2: two golfers share a group in at most one week
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            together = []
            for w in range(n_weeks):
                same = model.new_bool_var(f"same_{g1}_{g2}_{w}")
                model.add(assign[g1][w] == assign[g2][w]).only_enforce_if(same)
                model.add(assign[g1][w] != assign[g2][w]).only_enforce_if(same.negated())
                together.append(same)
            model.add(sum(together) <= 1)

    return model, {"assign": assign}
