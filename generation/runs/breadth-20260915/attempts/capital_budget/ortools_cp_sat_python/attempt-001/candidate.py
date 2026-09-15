from ortools.sat.python import cp_model


def build(instance):
    budget, npv, cash_flow = instance["budget"], instance["npv"], instance["cash_flow"]
    n = len(npv)
    model = cp_model.CpModel()
    chosen = [model.new_bool_var(f"x_{i}") for i in range(n)]
    total = model.new_int_var(0, sum(npv), "z")
    model.add(sum(cash_flow[i] * chosen[i] for i in range(n)) <= budget)
    model.add(total == sum(npv[i] * chosen[i] for i in range(n)))
    model.maximize(total)
    return model, {"z": total, "x": chosen}
