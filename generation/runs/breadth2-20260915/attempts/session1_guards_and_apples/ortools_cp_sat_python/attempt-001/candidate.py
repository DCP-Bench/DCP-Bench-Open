from ortools.sat.python import cp_model


def build(instance):
    gates = instance["num_gates"]
    model = cp_model.CpModel()
    apples = [model.new_int_var(0, 100, f"apples_{i}") for i in range(gates + 1)]
    model.add(apples[gates] == 1)
    for i in range(1, gates + 1):
        model.add(apples[i - 1] == 2 * (apples[i] + 1))
    return model, {"apples": apples}
