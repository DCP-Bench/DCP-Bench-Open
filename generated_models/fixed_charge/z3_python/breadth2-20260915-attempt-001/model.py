import z3


def build(instance):
    machines, products = instance["num_machines"], instance["num_products"]
    resources = len(instance["resources"])
    renting_cost, capacity = instance["renting_cost"], instance["capacity"]
    ceiling, profit_and_machine, use = instance["max_production"], instance["product"], instance["use"]
    rent = [z3.Bool(f"rent_{m}") for m in range(machines)]
    rented = [z3.If(rent[m], 1, 0) for m in range(machines)]
    produce = [z3.Int(f"produce_{p}") for p in range(products)]
    total = z3.Int("z")
    constraints = [p >= 0 for p in produce] + [p <= ceiling for p in produce]
    constraints += [total >= 0, total <= 10000]
    constraints.append(total == (z3.Sum([profit_and_machine[p][0] * produce[p] for p in range(products)])
                                 - z3.Sum([renting_cost[m] * rented[m] for m in range(machines)])))
    for r in range(resources):
        constraints.append(z3.Sum([use[p][r] * produce[p] for p in range(products)]) <= capacity[r])
    for p in range(products):
        constraints.append(produce[p] <= ceiling * rented[p])
    return constraints, {"z": total}, ("maximize", total)
