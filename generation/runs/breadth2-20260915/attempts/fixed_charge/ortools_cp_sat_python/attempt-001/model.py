from ortools.sat.python import cp_model


def build(instance):
    machines, products = instance["num_machines"], instance["num_products"]
    resources = len(instance["resources"])
    renting_cost, capacity = instance["renting_cost"], instance["capacity"]
    ceiling, profit_and_machine, use = instance["max_production"], instance["product"], instance["use"]
    model = cp_model.CpModel()
    rent = [model.new_bool_var(f"rent_{m}") for m in range(machines)]
    produce = [model.new_int_var(0, ceiling, f"produce_{p}") for p in range(products)]
    total = model.new_int_var(0, 10000, "z")
    model.add(total == (sum(profit_and_machine[p][0] * produce[p] for p in range(products))
                        - sum(renting_cost[m] * rent[m] for m in range(machines))))
    for r in range(resources):
        model.add(sum(use[p][r] * produce[p] for p in range(products)) <= capacity[r])
    for p in range(products):
        model.add(produce[p] <= ceiling * rent[p])
    model.maximize(total)
    return model, {"z": total}
