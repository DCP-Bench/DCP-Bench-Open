"""Fixed charge: decide which machines to rent and how much of each product to make, for maximum profit."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    machines = instance["machines"]    # machine indices
    products = instance["products"]    # product indices
    resources = instance["resources"]  # resource indices (labour, cloth)
    renting_cost = instance["renting_cost"]
    capacity = instance["capacity"]
    product = instance["product"]      # product[p] = [profit per unit, machine it needs]
    use = instance["use"]              # use[p][r]: amount of resource r one unit of p needs
    max_production = instance["max_production"]

    model = gp.Model("fixed_charge")

    # rent[m] is 1 when machine m is rented; produce[p] is how much of product p is made.
    rent = model.addVars(machines, vtype=GRB.BINARY, name="rent")
    produce = model.addVars(products, lb=0, ub=max_production, vtype=GRB.INTEGER, name="produce")

    # Production uses no more labour or cloth than is available.
    for r in resources:
        model.addConstr(gp.quicksum(use[p][r] * produce[p] for p in products) <= capacity[r],
                        name=f"capacity[{r}]")

    # A product can be made only if the machine it needs is rented.
    for p in products:
        model.addConstr(produce[p] <= max_production * rent[product[p][1]], name=f"machine[{p}]")

    # z is the profit on the products minus the rent of the machines. The
    # reference model gives it the domain 0..10000, which is mirrored here.
    z = model.addVar(lb=0, ub=10000, vtype=GRB.INTEGER, name="z")
    model.addConstr(z == gp.quicksum(product[p][0] * produce[p] for p in products)
                    - gp.quicksum(renting_cost[m] * rent[m] for m in machines), name="profit")

    # Maximise the profit.
    model.setObjective(z, GRB.MAXIMIZE)

    return model, {"z": z}
