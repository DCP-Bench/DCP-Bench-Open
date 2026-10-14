# Fixed-charge production: a company makes products that each need labor and
# cloth (both in limited supply) and can only be made on a rented machine.
# Choose which machines to rent and how many of each product to make so that the
# profit from the products, less the machine rental costs, is as large as possible.
from hermax.model import Model


def build(instance):
    renting_cost = instance["renting_cost"]  # renting_cost[k] = cost of renting machine k
    capacity = instance["capacity"]  # capacity[r] = available amount of resource r (labor, cloth)
    max_production = instance["max_production"]  # most units of one product the problem allows
    product = instance["product"]  # product[p] = [profit per unit, machine needed]
    use = instance["use"]  # use[p][r] = amount of resource r that one unit of p uses
    num_products = len(product)
    num_machines = len(renting_cost)
    num_resources = len(capacity)
    profit = [product[p][0] for p in range(num_products)]
    machine = [product[p][1] for p in range(num_products)]

    # No product can be made in more units than its scarcest resource allows
    # (or than max_production); this is implied by the capacity constraints and
    # keeps the integer domains, which hermax encodes, small.
    bound = []
    for p in range(num_products):
        limit = max_production
        for r in range(num_resources):
            if use[p][r] > 0:
                limit = min(limit, capacity[r] // use[p][r])
        bound.append(max(limit, 1))

    m = Model()
    # rent[k] = 1 when machine k is rented (an integer, so that the rental cost
    # can be scaled and added up below)
    rent = m.int_vector("rent", num_machines, 0, 1)
    # produce[p] = units made of product p
    produce = m.int_vector("produce", num_products, 0, max(bound))
    for p in range(num_products):
        m &= (produce[p] <= bound[p])

    # resource use stays within what is available
    for r in range(num_resources):
        m &= (sum(use[p][r] * produce[p] for p in range(num_products)) <= capacity[r])

    # a product can only be made when the machine it needs is rented
    for p in range(num_products):
        m &= (~(produce[p] >= 1) | (rent[machine[p]] >= 1))

    # Maximise profit minus rental costs. A soft clause pays when its literal is
    # false: missing out on the s-th unit of product p costs its unit profit
    # (literal "produce[p] >= s"), and renting a machine costs its rent
    # (literal "not rented"). The total paid is a constant minus the profit,
    # so minimising it maximises the profit.
    for p in range(num_products):
        for s in range(1, bound[p] + 1):
            m.obj[profit[p]] += (produce[p] >= s)
    for k in range(num_machines):
        m.obj[renting_cost[k]] += ~(rent[k] >= 1)

    # z is the declared output: the profit made, i.e. revenue - rental. Each
    # side is added up with sum_var, which builds it from narrow partial sums;
    # writing the whole thing as one weighted equation over all the unit
    # literals is far slower to encode.
    revenue = m.sum_var([m.scale(produce[p], profit[p]) for p in range(num_products) if profit[p] > 0])
    rental = m.sum_var([m.scale(rent[k], renting_cost[k]) for k in range(num_machines) if renting_cost[k] > 0])
    z = m.int("z", 0, sum(profit[p] * bound[p] for p in range(num_products)))
    m &= (revenue - rental == z)

    return m, {"z": z}
