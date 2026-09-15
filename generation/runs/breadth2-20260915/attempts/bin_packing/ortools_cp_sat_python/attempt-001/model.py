from ortools.sat.python import cp_model


def build(instance):
    weights, capacity = instance["weights"], instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)
    model = cp_model.CpModel()
    bins = [model.new_int_var(0, num_bins - 1, f"bin_{j}") for j in range(n)]
    # in_bin[j][i] reifies bins[j] == i, which CP-SAT needs stated explicitly.
    in_bin = [[model.new_bool_var(f"in_{j}_{i}") for i in range(num_bins)] for j in range(n)]
    for j in range(n):
        for i in range(num_bins):
            model.add(bins[j] == i).only_enforce_if(in_bin[j][i])
            model.add(bins[j] != i).only_enforce_if(~in_bin[j][i])
        model.add_exactly_one(in_bin[j])
    for i in range(n):
        if i < num_bins:
            model.add(sum(weights[j] * in_bin[j][i] for j in range(n)) <= capacity)
    return model, {"bins": bins}
