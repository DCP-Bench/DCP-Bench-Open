from ortools.sat.python import cp_model


def build(instance):
    n, least, most = instance["n"], instance["m1"], instance["m2"]
    model = cp_model.CpModel()
    steps = [model.new_int_var(0, most, f"step_{i}") for i in range(n)]
    taken = [model.new_bool_var(f"taken_{i}") for i in range(n)]
    model.add(sum(steps) == n)
    for i in range(n):
        model.add(steps[i] >= least).only_enforce_if(taken[i])
        model.add(steps[i] == 0).only_enforce_if(~taken[i])
    for i in range(1, n):
        # Once a move is empty, every later one is too.
        model.add_implication(~taken[i - 1], ~taken[i])
    return model, {"steps": steps}
