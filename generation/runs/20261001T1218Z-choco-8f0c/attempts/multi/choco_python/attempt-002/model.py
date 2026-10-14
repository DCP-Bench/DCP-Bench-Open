# Multi-commodity transportation: ship products from origins to destinations, within each
# origin's supply and the limit on each origin-destination route, so that every demand is
# met at the lowest total shipping cost.
from pychoco.model import Model


def build(instance):
    supply = instance["supply"]  # supply[i][p] = supply of product p at origin i
    demand = instance["demand"]  # demand[j][p] = demand of product p at destination j
    limit = instance["limit"]  # limit[i][j] = most that can be shipped from origin i to destination j
    cost = instance["cost"]  # cost[i][j][p] = cost of shipping one unit of product p from i to j
    n_origins = len(supply)
    n_destinations = len(demand)
    n_products = len(supply[0])
    max_supply = max(max(row) for row in supply)  # no single shipment can exceed the largest supply
    max_total_cost = sum(sum(row) for row in supply) * max(max(row) for matrix in cost for row in matrix)

    model = Model()

    # x[i][j][p] = units of product p shipped from origin i to destination j
    x = [[[model.intvar(0, max_supply, name=f"x_{i}_{j}_{p}") for p in range(n_products)]
          for j in range(n_destinations)] for i in range(n_origins)]

    # an origin cannot ship more of a product than its supply
    for i in range(n_origins):
        for p in range(n_products):
            model.sum([x[i][j][p] for j in range(n_destinations)], "<=", supply[i][p]).post()

    # Every destination receives at least its demand of each product. When no shipping cost is
    # negative, shipping more than the demand cannot lower the cost, and removing the excess
    # keeps every supply and route limit satisfied. The optimal cost is then reached with exactly
    # the demand delivered, so the equality is used; it only drops plans that are not cheaper.
    exact_delivery = min(c for matrix in cost for row in matrix for c in row) >= 0
    for j in range(n_destinations):
        for p in range(n_products):
            model.sum([x[i][j][p] for i in range(n_origins)], "=" if exact_delivery else ">=", demand[j][p]).post()

    # the total shipped on each route (origin to destination) is within its limit
    for i in range(n_origins):
        for j in range(n_destinations):
            model.sum(x[i][j], "<=", limit[i][j]).post()

    # total shipping cost, the quantity to minimise
    flat_x = [x[i][j][p] for i in range(n_origins) for j in range(n_destinations) for p in range(n_products)]
    flat_cost = [cost[i][j][p] for i in range(n_origins) for j in range(n_destinations) for p in range(n_products)]
    total_cost = model.intvar(0, max_total_cost, name="total_cost")
    model.scalar(flat_x, flat_cost, "=", total_cost).post()

    # Tie-break between plans of equal cost. Only the cost is declared, but Choco enumerates
    # every optimal plan, and a transportation problem has very many of them. The objective
    # variable therefore ranks plans first by cost, then by a weighted sum of the shipments
    # (weight k + 1 for the k-th shipment); the weighted sum stays below `cost_weight`, so the
    # cheapest plan still has the minimal total_cost, the declared output.
    tie_weights = [k + 1 for k in range(len(flat_x))]
    cost_weight = sum(tie_weights) * max_supply + 1
    ranked_cost = model.intvar(0, cost_weight * max_total_cost + cost_weight - 1, name="ranked_cost")
    model.scalar(flat_x, [cost_weight * c + w for c, w in zip(flat_cost, tie_weights)], "=", ranked_cost).post()

    return model, {"total_cost": total_cost}, ("minimize", ranked_cost)
