# Revenue maximization: choose how many units of each itinerary package to sell,
# given flight legs with limited seats, so that total revenue is maximized.
import mip


def build(instance):
    demand = instance["demand"]          # estimated demand per package
    revenue = instance["revenue"]        # price per unit of each package
    seats = instance["available_seats"]  # passenger capacity of each flight leg
    delta = instance["delta"]            # delta[p][l] = 1 if package p uses leg l

    n_packages = len(demand)
    n_legs = len(seats)

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # units of each package to sell, at most its estimated demand
    sell = [
        model.add_var(f"sell_{p}", lb=0, ub=demand[p], var_type=mip.INTEGER)
        for p in range(n_packages)
    ]
    # total revenue; its upper bound is the revenue if every package sold its full demand
    max_revenue = model.add_var(
        "max_revenue", lb=0,
        ub=sum(revenue[p] * demand[p] for p in range(n_packages)),
        var_type=mip.INTEGER,
    )

    # the passenger seats reserved on each leg must not exceed the leg's available seats
    for l in range(n_legs):
        model.add_constr(
            mip.xsum(sell[p] for p in range(n_packages) if delta[p][l] == 1) <= seats[l],
            f"seats_leg_{l}",
        )

    # the total revenue is the sum of the price times the units sold of each package
    model.add_constr(
        max_revenue == mip.xsum(revenue[p] * sell[p] for p in range(n_packages)),
        "total_revenue",
    )

    model.objective = max_revenue
    model.verbose = 0
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    outputs = {
        "max_revenue": max_revenue,
        "packages_to_sell": sell,
    }
    return model, outputs
