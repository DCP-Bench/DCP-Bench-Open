# Fixed-charge production planning: choose how much of each product to make and which machines to rent,
# to maximise profit minus machine rental costs.
from pyscipopt import Model, quicksum


def build(instance):
    n_prod = instance["num_products"]
    n_mach = instance["num_machines"]
    n_res = len(instance["resources"])

    # per product: profit per unit, and the machine that must be rented to make it
    # (product[j] = [profit, machine]); per product and resource: use[j][r] units of resource r per unit
    profit = [instance["product"][j][0] for j in range(n_prod)]
    machine_of = [instance["product"][j][1] for j in range(n_prod)]
    use = instance["use"]
    capacity = instance["capacity"]
    rent_cost = instance["renting_cost"]
    max_prod = instance["max_production"]

    m = Model()

    # make[j] = number of units of product j produced, between 0 and max_production
    make = [m.addVar(name=f"make_{j}", vtype="I", lb=0, ub=max_prod) for j in range(n_prod)]
    # rent[i] = 1 if machine i is rented
    rent = [m.addVar(name=f"rent_{i}", vtype="B") for i in range(n_mach)]
    # profit z: the objective value, profit from products minus rental costs
    z = m.addVar(name="z", vtype="I", lb=None, ub=None)

    # labor and cloth used by all products stay within the capacity of each resource
    for r in range(n_res):
        # resource capacity limit for resource r
        m.addCons(quicksum(use[j][r] * make[j] for j in range(n_prod)) <= capacity[r])

    # a product can be made only if the machine it needs is rented
    for j in range(n_prod):
        # if machine machine_of[j] is not rented, product j is not made
        m.addConsIndicator(make[j] <= 0, binvar=rent[machine_of[j]], activeone=False)

    # profit is the product revenue minus the rental cost of the machines
    # (the revenue of each product is its profit per unit times its quantity)
    m.addCons(z == quicksum(profit[j] * make[j] for j in range(n_prod))
              - quicksum(rent_cost[i] * rent[i] for i in range(n_mach)))

    m.setObjective(z, "maximize")

    return m, {"z": z}
