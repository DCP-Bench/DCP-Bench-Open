# Fixed charge: a company makes shirts, shorts and pants and must rent a machine
# for each product it manufactures. Maximise profit (excluding renting) minus rental costs.
from paramita.modelling import Bool, If


def build(instance):
    num_products = instance["num_products"]
    num_machines = instance["num_machines"]
    resources = instance["resources"]
    capacity = instance["capacity"]
    use = instance["use"]              # use[p][r]: amount of resource r per unit of product p
    profit = [instance["product"][p][0] for p in range(num_products)]    # profit per unit (excluding renting)
    machine_of = [instance["product"][p][1] for p in range(num_products)]  # machine that product p needs
    renting_cost = instance["renting_cost"]

    # Production limit of each product: the instance's max_production, and no more units
    # than any resource allows (capacity[r] // use[p][r] for the resources the product uses).
    top = []
    for p in range(num_products):
        bound = instance["max_production"]
        for r in resources:
            if use[p][r] > 0:
                bound = min(bound, capacity[r] // use[p][r])
        top.append(bound)

    # Production of product p is a binary number: units[p] = sum of 2^k * bit[p][k].
    bits = [[Bool(f"units_{p}_bit_{k}") for k in range(max(top[p], 1).bit_length())]
            for p in range(num_products)]
    units = [sum(2 ** k * b for k, b in enumerate(bits[p])) for p in range(num_products)]
    # y[m] = 1 if machine m is rented
    y = [Bool(f"rent_{m}") for m in range(num_machines)]
    cons = []

    # production limit of each product
    for p in range(num_products):
        cons.append(units[p] <= top[p])

    # labor and cloth: the products together use no more than the capacity of each resource
    for r in resources:
        cons.append(sum(use[p][r] * units[p] for p in range(num_products)) <= capacity[r])

    # products can only be manufactured by renting their machine
    for p in range(num_products):
        cons.append(If(units[p] >= 1, y[machine_of[p]]))

    # profit excluding renting, minus the renting cost of the machines
    z = sum(profit[p] * units[p] for p in range(num_products)) \
        - sum(renting_cost[m] * y[m] for m in range(num_machines))
    return cons, {"z": z}, ("maximize", z)
