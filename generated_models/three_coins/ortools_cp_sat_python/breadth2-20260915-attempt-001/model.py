from ortools.sat.python import cp_model


def build(instance):
    initial, moves = instance["init"], instance["num_moves"]
    n = len(initial)
    model = cp_model.CpModel()
    steps = [[model.new_bool_var(f"s_{m}_{j}") for j in range(n)] for m in range(moves + 1)]
    for j in range(n):
        model.add(steps[0][j] == initial[j])
    for m in range(1, moves + 1):
        flips = []
        for j in range(n):
            flip = model.new_bool_var(f"flip_{m}_{j}")
            model.add(steps[m][j] != steps[m - 1][j]).only_enforce_if(flip)
            model.add(steps[m][j] == steps[m - 1][j]).only_enforce_if(~flip)
            flips.append(flip)
        model.add(sum(flips) == 1)
    # The last row is all heads or all tails.
    all_tails = model.new_bool_var("all_tails")
    model.add(sum(steps[moves]) == n).only_enforce_if(all_tails)
    model.add(sum(steps[moves]) == 0).only_enforce_if(~all_tails)
    return model, {"steps": steps}
