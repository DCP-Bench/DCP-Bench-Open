from ortools.sat.python import cp_model


def build(instance):
    n, adjacency = instance["n"], instance["adj"]
    model = cp_model.CpModel()
    chosen = [model.new_bool_var(f"c_{i}") for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if adjacency[i][j] == 0:
                model.add_at_most_one([chosen[i], chosen[j]])
    model.maximize(sum(chosen))
    return model, {"c": chosen}
