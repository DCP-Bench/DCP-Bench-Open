# Fixed charge production planning (shirts, shorts, pants).
# The company manufactures shirts, shorts and pants. Each product requires a number of
# hours of labor and an amount of cloth, and the company has a limited capacity of both.
# All products can be manufactured only by renting an appropriate machine. The profit on
# the products (excluding the cost of renting the equipment) is known. Maximise the profit
# z: the sum of product profits minus the rental cost of the machines used.
import mip


def build(instance):
    num_products = instance["num_products"]
    num_machines = instance["num_machines"]
    num_resources = len(instance["resources"])
    capacity = instance["capacity"]
    max_production = instance["max_production"]
    renting_cost = instance["renting_cost"]
    use = instance["use"]
    profit = [instance["product"][p][0] for p in range(num_products)]

    # The machine each product needs, keyed by product id.
    machine_of_id = {
        instance["shirt"]: instance["shirtM"],
        instance["shorts"]: instance["shortM"],
        instance["pants"]: instance["pantM"],
    }
    machine_of = [machine_of_id[instance["products"][p]] for p in range(num_products)]

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # Production quantity of each product, bounded by the largest production in the data.
    x = [
        model.add_var(f"x_{p}", lb=0, ub=max_production, var_type=mip.INTEGER)
        for p in range(num_products)
    ]
    # Whether each machine is rented.
    rent = [
        model.add_var(f"rent_{m}", var_type=mip.BINARY)
        for m in range(num_machines)
    ]

    # The products can be manufactured only by renting an appropriate machine.
    for p in range(num_products):
        model.add_constr(x[p] <= max_production * rent[machine_of[p]], f"needs_machine_{p}")

    # The company has a limited capacity of each resource (labor hours and cloth).
    for r in range(num_resources):
        model.add_constr(
            mip.xsum(use[p][r] * x[p] for p in range(num_products)) <= capacity[r],
            f"capacity_{r}",
        )

    # The profit z is the product profit minus the rental cost of the machines.
    # z is integer with bounds from the data: the lowest is renting every machine
    # and producing nothing, the highest is producing the maximum of every product.
    z_lb = -sum(renting_cost)
    z_ub = sum(profit[p] * max_production for p in range(num_products))
    z = model.add_var("z", lb=z_lb, ub=z_ub, var_type=mip.INTEGER)
    model.add_constr(
        z == mip.xsum(profit[p] * x[p] for p in range(num_products))
        - mip.xsum(renting_cost[m] * rent[m] for m in range(num_machines)),
        "profit",
    )

    model.objective = z
    return model, {"z": z}
