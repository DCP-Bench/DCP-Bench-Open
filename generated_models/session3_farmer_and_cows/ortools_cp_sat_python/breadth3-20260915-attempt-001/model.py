from ortools.sat.python import cp_model


def build(instance):
    cows, sons = instance["num_cows"], instance["num_sons"]
    per_son = instance["cows_per_son"]
    milk = list(range(1, cows + 1))
    share = sum(milk) // sons
    model = cp_model.CpModel()
    assignment = [model.new_int_var(0, sons - 1, f"a_{i}") for i in range(cows)]
    # got[i][son] reifies assignment[i] == son.
    got = [[model.new_bool_var(f"got_{i}_{s}") for s in range(sons)] for i in range(cows)]
    for i in range(cows):
        for s in range(sons):
            model.add(assignment[i] == s).only_enforce_if(got[i][s])
            model.add(assignment[i] != s).only_enforce_if(~got[i][s])
        model.add_exactly_one(got[i])
    for son in range(sons):
        model.add(sum(got[i][son] for i in range(cows)) == per_son[son])
        model.add(sum(milk[i] * got[i][son] for i in range(cows)) == share)
    return model, {"cow_assignments": assignment}
