from ortools.sat.python import cp_model


def build(instance):
    n = instance["n"]
    model = cp_model.CpModel()
    queens = [model.new_int_var(1, n, f"queens_{i}") for i in range(n)]
    model.add_all_different(queens)
    model.add_all_different([q - i for i, q in enumerate(queens)])
    model.add_all_different([q + i for i, q in enumerate(queens)])
    return model, {"queens": queens}
