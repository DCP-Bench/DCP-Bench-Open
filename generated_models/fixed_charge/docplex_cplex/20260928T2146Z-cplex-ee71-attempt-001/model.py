"""Fixed charge: decide which machines to rent and how much of each product to make, for maximum profit."""
from docplex.mp.model import Model


def build(instance):
    machines = instance["machines"]    # machine indices
    products = instance["products"]    # product indices
    resources = instance["resources"]  # resource indices (labour, cloth)
    renting_cost = instance["renting_cost"]
    capacity = instance["capacity"]
    product = instance["product"]      # product[p] = [profit per unit, machine it needs]
    use = instance["use"]              # use[p][r]: amount of resource r one unit of p needs
    max_production = instance["max_production"]

    model = Model("fixed_charge")

    # rent[m] is 1 when machine m is rented; produce[p] is how much of product p is made.
    rent = {m: model.binary_var(name=f"rent_{m}") for m in machines}
    produce = {p: model.integer_var(0, max_production, name=f"produce_{p}") for p in products}

    # Production uses no more labour or cloth than is available.
    for r in resources:
        model.add_constraint(model.sum(use[p][r] * produce[p] for p in products) <= capacity[r],
                             ctname=f"capacity_{r}")

    # A product can be made only if the machine it needs is rented.
    for p in products:
        model.add_constraint(produce[p] <= max_production * rent[product[p][1]], ctname=f"machine_{p}")

    # z is the profit on the products minus the rent of the machines. The
    # reference model gives it the domain 0..10000, which is mirrored here.
    z = model.integer_var(0, 10000, name="z")
    model.add_constraint(z == model.sum(product[p][0] * produce[p] for p in products)
                         - model.sum(renting_cost[m] * rent[m] for m in machines), ctname="profit")

    # Maximise the profit.
    model.maximize(z)

    return model, {"z": z}
