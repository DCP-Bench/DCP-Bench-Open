# Multi-commodity transportation problem: ship each product p from each origin i to
# each destination j, at ShippingCost[i][j][p] per unit, so that the total cost is
# minimised. The model reads the origins, destinations and products from the instance.
import mip


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    limit = instance["limit"]
    cost = instance["cost"]
    n_origins = len(supply)
    n_products = len(supply[0])
    n_destinations = len(demand)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Units of product p shipped from origin i to destination j.
    x = [
        [
            [
                model.add_var(
                    name=f"x_{i}_{j}_{p}",
                    lb=0,
                    ub=min(supply[i][p], demand[j][p], limit[i][j]),
                    var_type=mip.INTEGER,
                )
                for p in range(n_products)
            ]
            for j in range(n_destinations)
        ]
        for i in range(n_origins)
    ]

    # The shipments of each product from an origin do not exceed its supply.
    for i in range(n_origins):
        for p in range(n_products):
            model.add_constr(
                mip.xsum(x[i][j][p] for j in range(n_destinations)) <= supply[i][p],
                name=f"supply_{i}_{p}",
            )

    # Each destination receives exactly its demand of each product.
    for j in range(n_destinations):
        for p in range(n_products):
            model.add_constr(
                mip.xsum(x[i][j][p] for i in range(n_origins)) == demand[j][p],
                name=f"demand_{j}_{p}",
            )

    # The total shipped on each lane, over all products, is within its limit.
    for i in range(n_origins):
        for j in range(n_destinations):
            model.add_constr(
                mip.xsum(x[i][j][p] for p in range(n_products)) <= limit[i][j],
                name=f"limit_{i}_{j}",
            )

    # Minimise the total shipping cost.
    total_cost = mip.xsum(
        cost[i][j][p] * x[i][j][p]
        for i in range(n_origins)
        for j in range(n_destinations)
        for p in range(n_products)
    )
    model.objective = total_cost

    return model, {"total_cost": total_cost}
