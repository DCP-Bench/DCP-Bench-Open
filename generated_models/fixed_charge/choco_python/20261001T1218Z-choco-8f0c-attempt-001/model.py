# Fixed-charge production: a company makes products that each use labor and cloth, can
# only make a product on a rented machine, and wants the largest profit after paying
# the rent of the machines it uses.
from pychoco.model import Model


def build(instance):
    num_machines = instance["num_machines"]
    num_products = instance["num_products"]
    renting_cost = instance["renting_cost"]  # renting_cost[m] = cost of renting machine m
    capacity = instance["capacity"]  # capacity[r] = available amount of resource r (labor, cloth)
    max_production = instance["max_production"]  # upper bound on the units of one product
    product = instance["product"]  # product[p] = [profit per unit, machine needed]
    use = instance["use"]  # use[p][r] = amount of resource r used by one unit of product p
    profit = [product[p][0] for p in range(num_products)]
    machine_of = [product[p][1] for p in range(num_products)]

    model = Model()

    # rent[m] = 1 if machine m is rented
    rent = [model.boolvar(name=f"rent_{m}") for m in range(num_machines)]
    # produce[p] = number of units made of product p
    produce = [model.intvar(0, max_production, name=f"produce_{p}") for p in range(num_products)]

    # the resources used by the production must not exceed the capacities
    for r in range(len(capacity)):
        model.scalar(produce, [use[p][r] for p in range(num_products)], "<=", capacity[r]).post()

    # a product can only be made if its machine is rented:
    # produce[p] <= max_production * rent[machine of p]
    for p in range(num_products):
        model.scalar([produce[p], rent[machine_of[p]]], [1, -max_production], "<=", 0).post()

    # profit = income of the products made - rent of the machines rented
    # (the bound 10000 on z is the problem's own)
    z = model.intvar(0, 10000, name="z")
    model.scalar(produce + rent, profit + [-cost for cost in renting_cost], "=", z).post()

    return model, {"z": z}, ("maximize", z)
