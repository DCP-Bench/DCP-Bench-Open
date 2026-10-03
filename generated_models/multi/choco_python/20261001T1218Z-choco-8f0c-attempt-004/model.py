# Multi-commodity transportation: ship products from origins to destinations, within each
# origin's supply and the limit on each origin-destination route, so that every demand is
# met at the lowest total shipping cost.
from pychoco.model import Model


def delivery_plans(units, caps, unit_costs):
    """Every way to ship exactly `units` units of one product to one destination.

    Origin i ships between 0 and caps[i] units at unit_costs[i] each. A plan is the list
    of shipments from the origins followed by their total cost.
    """
    plans = []

    def extend(origin, left, shipped):
        if origin == len(caps):
            if left == 0:
                plans.append(shipped + [sum(c * v for c, v in zip(unit_costs, shipped))])
            return
        for amount in range(min(caps[origin], left) + 1):
            extend(origin + 1, left - amount, shipped + [amount])

    extend(0, units, [])
    return plans


def build(instance):
    supply = instance["supply"]  # supply[i][p] = supply of product p at origin i
    demand = instance["demand"]  # demand[j][p] = demand of product p at destination j
    limit = instance["limit"]  # limit[i][j] = most that can be shipped from origin i to destination j
    cost = instance["cost"]  # cost[i][j][p] = cost of shipping one unit of product p from i to j
    n_origins = len(supply)
    n_destinations = len(demand)
    n_products = len(supply[0])
    max_total_cost = sum(sum(row) for row in supply) * max(max(row) for matrix in cost for row in matrix)

    # A shipping cost is a price per unit, so it is not negative. Shipping more than a
    # destination demands then never lowers the cost, and removing the excess keeps every
    # supply and route limit satisfied: some optimal plan delivers exactly the demand.
    assert min(c for matrix in cost for row in matrix for c in row) >= 0, "shipping costs must not be negative"

    model = Model()

    # x[i][j][p] = units of product p shipped from origin i to destination j. It cannot exceed
    # the origin's supply of p, the route limit, or what the destination demands.
    most = [[[min(supply[i][p], limit[i][j], demand[j][p]) for p in range(n_products)]
             for j in range(n_destinations)] for i in range(n_origins)]
    x = [[[model.intvar(0, most[i][j][p], name=f"x_{i}_{j}_{p}") for p in range(n_products)]
          for j in range(n_destinations)] for i in range(n_origins)]

    # Every destination receives its demand of each product, at a delivery cost that depends on
    # which origins it comes from. The table lists every split of the demand among the origins
    # with the cost of that split, so the cost of a delivery is bounded below by its cheapest
    # split before any shipment is fixed. A plain sum of unit cost times shipment, as in an
    # earlier version of this model, did not finish the larger instances within the time limit.
    delivery_cost = []
    for j in range(n_destinations):
        for p in range(n_products):
            shipments = [x[i][j][p] for i in range(n_origins)]
            plans = delivery_plans(demand[j][p], [most[i][j][p] for i in range(n_origins)],
                                   [cost[i][j][p] for i in range(n_origins)])
            cost_jp = model.intvar(min(plan[-1] for plan in plans), max(plan[-1] for plan in plans),
                                   name=f"delivery_cost_{j}_{p}")
            model.table(shipments + [cost_jp], plans).post()
            delivery_cost.append(cost_jp)

    # an origin cannot ship more of a product than its supply
    for i in range(n_origins):
        for p in range(n_products):
            model.sum([x[i][j][p] for j in range(n_destinations)], "<=", supply[i][p]).post()

    # the total shipped on each route (origin to destination) is within its limit
    for i in range(n_origins):
        for j in range(n_destinations):
            model.sum(x[i][j], "<=", limit[i][j]).post()

    # total shipping cost, the quantity to minimise
    total_cost = model.intvar(0, max_total_cost, name="total_cost")
    model.sum(delivery_cost, "=", total_cost).post()

    # Tie-break between plans of equal cost. Only the cost is declared, but Choco enumerates
    # every optimal plan, and plans of equal cost made that enumeration run out of time on the
    # larger instances. The objective variable therefore ranks plans first by cost, then by a
    # weighted sum of the shipments (weight k + 1 for the k-th shipment). The weighted sum stays
    # below `cost_weight`, so the cheapest plan still has the minimal total_cost, the declared
    # output.
    flat_x = [x[i][j][p] for i in range(n_origins) for j in range(n_destinations) for p in range(n_products)]
    tie_weights = [k + 1 for k in range(len(flat_x))]
    flat_most = [most[i][j][p] for i in range(n_origins) for j in range(n_destinations) for p in range(n_products)]
    tie_break_max = sum(w * m for w, m in zip(tie_weights, flat_most))
    tie_break = model.intvar(0, tie_break_max, name="tie_break")
    model.scalar(flat_x, tie_weights, "=", tie_break).post()
    cost_weight = tie_break_max + 1
    ranked_cost = model.intvar(0, cost_weight * max_total_cost + tie_break_max, name="ranked_cost")
    model.scalar([total_cost, tie_break], [cost_weight, 1], "=", ranked_cost).post()

    return model, {"total_cost": total_cost}, ("minimize", ranked_cost)
