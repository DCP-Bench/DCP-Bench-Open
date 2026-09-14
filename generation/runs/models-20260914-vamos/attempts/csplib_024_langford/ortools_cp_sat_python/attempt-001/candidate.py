from ortools.sat.python import cp_model


def build(instance):
    k = instance["k"]
    model = cp_model.CpModel()
    # position[i - 1] and position[k + i - 1] hold the two places of value i.
    position = [model.new_int_var(0, 2 * k - 1, f"position_{j}") for j in range(2 * k)]
    sol = [model.new_int_var(1, k, f"sol_{j}") for j in range(2 * k)]
    model.add_all_different(position)
    for i in range(1, k + 1):
        model.add(position[i + k - 1] == position[i - 1] + i + 1)
        model.add_element(position[i - 1], sol, i)
        model.add_element(position[k + i - 1], sol, i)
    return model, {"sol": sol}
