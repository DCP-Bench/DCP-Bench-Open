from ortools.sat.python import cp_model


def build(instance):
    free = instance["m"]
    n = len(free)
    model = cp_model.CpModel()
    booked = [[model.new_bool_var(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    for i in range(n):
        model.add(sum(free[i][j] * booked[i][j] for j in range(n)) == 1)
        model.add_exactly_one(booked[i])
        model.add_exactly_one(booked[j][i] for j in range(n))
    return model, {"x": booked}
