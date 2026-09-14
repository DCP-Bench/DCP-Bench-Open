from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    model = cp_model.CpModel()
    costas = [model.new_int_var(1, n, f"costas_{i}") for i in range(n)]
    model.add_all_different(costas)
    # Row i of the difference triangle holds costas[j] - costas[j - i - 1].
    for i in range(n - 2):
        model.add_all_different([costas[j] - costas[j - i - 1] for j in range(i + 1, n)])
    return model, {"costas": costas}
