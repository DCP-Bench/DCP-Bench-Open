# Diet problem: choose whole numbers of each food (chocolate cake, chocolate ice cream,
# cola, pineapple cheesecake) that meet the minimum calories, chocolate, sugar and fat
# requirements at the lowest total cost. Output: the optimal cost of the diet (cost).
import mip

# Nutrient content of one unit of each food. This table is the problem's fixed data
# (the description's table), not part of the instance. Columns: calories, chocolate
# (ounces), sugar (ounces), fat (ounces). The instance's limits use the same order.
NUTRIENTS = [
    [400, 3, 2, 2],  # Chocolate cake (1 slice)
    [200, 2, 2, 4],  # Chocolate ice cream (1 scoop)
    [150, 0, 4, 1],  # Cola (1 bottle)
    [500, 0, 4, 5],  # Pineapple cheesecake (1 piece)
]


def build(instance):
    n = instance["n"]
    price = instance["price"]
    limits = instance["limits"]
    nutrients = len(limits)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.verbose = 0
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    # Upper bound on the number of units of each food. Every nutrient content is
    # non-negative and every price is non-negative, so if a food is bought more often
    # than needed to meet the largest requirement it can cover alone, cutting it back
    # to that point keeps the diet feasible and does not raise the cost.
    ub = []
    for i in range(n):
        bound = 0
        for j in range(nutrients):
            if NUTRIENTS[i][j] > 0:
                bound = max(bound, -(-limits[j] // NUTRIENTS[i][j]))
        ub.append(bound)

    # number of units of each food bought, from the instance's food count
    x = [model.add_var(f"x_{i}", lb=0, ub=ub[i], var_type=mip.INTEGER) for i in range(n)]

    # the total cost of the diet is at most the price of buying every food at its bound
    cost = model.add_var(
        "cost", lb=0, ub=sum(price[i] * ub[i] for i in range(n)), var_type=mip.INTEGER
    )

    # the diet must provide at least the required calories, chocolate, sugar and fat
    for j in range(nutrients):
        model.add_constr(
            mip.xsum(NUTRIENTS[i][j] * x[i] for i in range(n)) >= limits[j],
            name=f"requirement_{j}",
        )

    # cost is the price of the foods bought
    model.add_constr(
        cost == mip.xsum(price[i] * x[i] for i in range(n)),
        name="total_cost",
    )

    # minimise the cost of the diet
    model.objective = cost

    return model, {"cost": cost}
