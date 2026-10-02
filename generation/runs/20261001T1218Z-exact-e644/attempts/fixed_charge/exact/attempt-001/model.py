# Fixed-charge production: a company makes shirts, shorts and pants from limited labor and cloth.
# Each product needs its own machine, which must be rented (a fixed charge) before the product can
# be made at all. Maximise the profit z: product profits minus the rent paid.
from exact import Exact


def build(instance):
    machines = instance["machines"]
    products = instance["products"]
    resources = instance["resources"]  # labor and cloth
    renting_cost = instance["renting_cost"]  # rent of each machine
    capacity = instance["capacity"]  # available amount of each resource
    max_production = instance["max_production"]  # upper bound on the amount made of a product
    product = instance["product"]  # product[p] = [profit per unit, machine needed by p]
    use = instance["use"]  # use[p][r] = amount of resource r used per unit of p

    solver = Exact()

    # rent[m] = 1 when machine m is rented
    rent = [f"rent_{m}" for m in machines]
    for name in rent:
        solver.addVariable(name, 0, 1)

    # produce[p] is the number of units of product p made
    produce = [f"produce_{p}" for p in products]
    for name in produce:
        solver.addVariable(name, 0, max_production)

    # z is the profit; its range 0..10000 is the one the reference declares
    solver.addVariable("z", 0, 10000)

    # the profit is the product profits minus the rent of the machines
    profit_terms = [(product[p][0], produce[p]) for p in products]
    rent_terms = [(-renting_cost[m], rent[m]) for m in machines]
    solver.addConstraint(profit_terms + rent_terms + [(-1, "z")], True, 0, True, 0)

    # the labor and cloth used cannot exceed what is available
    for r in resources:
        solver.addConstraint([(use[p][r], produce[p]) for p in products], False, 0, True, capacity[r])

    # a product can be made only on a rented machine: produce[p] <= max_production * rent[machine]
    for p in products:
        solver.addConstraint([(1, produce[p]), (-max_production, rent[product[p][1]])], False, 0, True, 0)

    return solver, {"z": "z"}, ("maximize", [(1, "z")])
