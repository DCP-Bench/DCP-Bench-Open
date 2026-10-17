# Fixed charge problem: a company manufactures shirts, shorts and pants. Each product
# requires hours of labor and an amount of cloth, the company has limited capacity of
# both, and every product can be made only by renting its machine. Maximise the profit
# on the products minus the renting cost of the machines.
import cvc5.pythonic as cz


def build(instance):
    num_products = instance["num_products"]
    num_machines = instance["num_machines"]
    num_resources = len(instance["capacity"])
    max_production = instance["max_production"]

    # Per product: the profit per unit and the machine it needs.
    profit = [instance["product"][p][0] for p in range(num_products)]
    machine_of = [instance["product"][p][1] for p in range(num_products)]

    x = [cz.Int(f"x_{p}") for p in range(num_products)]
    rent = [cz.Bool(f"rent_{m}") for m in range(num_machines)]
    z = cz.Int("z")

    constraints = []

    # Production bounds from the instance.
    for p in range(num_products):
        constraints += [x[p] >= 0, x[p] <= max_production]

    # A product can be manufactured only by renting its machine.
    for p in range(num_products):
        constraints.append(cz.Implies(x[p] > 0, rent[machine_of[p]]))

    # Labor and cloth capacities: each product uses use[p][r] of resource r per unit.
    for r in range(num_resources):
        constraints.append(
            cz.Sum([instance["use"][p][r] * x[p] for p in range(num_products)])
            <= instance["capacity"][r]
        )

    # Objective: profit on the products minus the renting cost of the rented machines.
    profit_expr = cz.Sum([profit[p] * x[p] for p in range(num_products)])
    rent_expr = cz.Sum(
        [instance["renting_cost"][m] * cz.If(rent[m], 1, 0) for m in range(num_machines)]
    )
    constraints.append(z == profit_expr - rent_expr)

    return constraints, {"z": z}, ("maximize", z)
