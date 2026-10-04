# Fixed-charge production (OPL fixed.mod): decide how many shirts, shorts and
# pants to make within the labor and cloth capacities, where a product can
# only be made after renting its machine, to maximise profit minus the rent.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    machines = instance["machines"]
    products = instance["products"]
    resources = instance["resources"]
    renting_cost = instance["renting_cost"]
    capacity = instance["capacity"]
    max_production = instance["max_production"]
    product = instance["product"]  # [profit, machine needed] per product
    use = instance["use"]  # use[p][r]: amount of resource r per unit of p

    pool = IDPool()

    # produce[p] is the number of units of product p made. The reference
    # allows up to max_production; no plan can make more than the scarcest
    # resource allows (capacity / use per unit), so that is the upper bound.
    # Order encoding: the bound and sum constraints read order literals.
    produce = {}
    for p in products:
        top = max_production
        for r in resources:
            if use[p][r] > 0:
                top = min(top, capacity[r] // use[p][r])
        produce[p] = Integer(f"produce_{p}", 0, max(top, 1), encoding="order",
                             vpool=pool)

    # rent[m] is 1 when machine m is rented.
    rent = {m: Integer(f"rent_{m}", 0, 1, vpool=pool) for m in machines}

    # z is the profit, the declared output. The reference gives it 0..10000;
    # it can be no more than the profit of making every product at its upper
    # bound, which narrows the domain without excluding any plan.
    most = sum(product[p][0] * produce[p].ub for p in products if product[p][0] > 0)
    z = Integer("z", 0, max(min(10000, most), 1), encoding="coupled", vpool=pool)

    engine = IntegerEngine(vars=list(produce.values()) + list(rent.values()) + [z],
                           vpool=pool)

    # z is the products' profit minus the rent of the machines rented (and,
    # by its domain, not negative).
    engine.add_linear(sum(product[p][0] * produce[p] for p in products)
                      - sum(renting_cost[m] * rent[m] for m in machines)
                      - z == 0)

    # The products made use no more labor or cloth than available.
    for r in resources:
        engine.add_linear(sum(use[p][r] * produce[p] for p in products) <= capacity[r])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # A product can only be made if its machine is rented.
    for p in products:
        m = product[p][1]
        formula.append([-produce[p].ge(1), rent[m].equals(1)])

    # Maximise the profit: each unit of product p not made (below its upper
    # bound) pays its profit, and renting machine m pays its rent, so RC2
    # minimises the shortfall from the profit of making everything for free.
    # A product with a negative profit pays for each unit made instead.
    for p in products:
        for v in range(1, produce[p].ub + 1):
            if product[p][0] > 0:
                formula.append([produce[p].ge(v)], weight=product[p][0])
            elif product[p][0] < 0:
                formula.append([-produce[p].ge(v)], weight=-product[p][0])
    for m in machines:
        if renting_cost[m] > 0:
            formula.append([-rent[m].equals(1)], weight=renting_cost[m])

    return formula, {"z": z}
