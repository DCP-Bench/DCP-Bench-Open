from ortools.sat.python import cp_model


def build(instance):
    count, qualified, cost = instance["nb_workers"], instance["Qualified"], instance["Cost"]
    model = cp_model.CpModel()
    hired = [model.new_bool_var(f"w_{i}") for i in range(count)]
    total = model.new_int_var(0, count * sum(cost), "total_cost")
    model.add(total == sum(cost[i] * hired[i] for i in range(count)))
    for task in qualified:
        model.add(sum(hired[worker - 1] for worker in task) >= 1)
    model.minimize(total)
    return model, {"total_cost": total, "workers": hired}
