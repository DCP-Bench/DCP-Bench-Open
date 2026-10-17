# Coins on an n by n grid (coins_grid): place coins so that every row and every column
# holds exactly c coins, at most one coin per cell. Minimise the sum of the quadratic
# horizontal distance from the main diagonal over all cells that hold a coin.
import mip


def build(instance):
    n = instance["n"]
    c = instance["c"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Coin placement: one binary per cell, so at most one coin per cell.
    x = [[model.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(n)] for i in range(n)]

    # Objective value: the sum of squared horizontal distances (j - i) of coins from the diagonal.
    # Largest possible value: c coins in each of n rows, each at distance at most n - 1.
    z = model.add_var("z", lb=0, ub=c * n * (n - 1) ** 2, var_type=mip.INTEGER)

    # In each row exactly c coins must be placed.
    for i in range(n):
        model += mip.xsum(x[i][j] for j in range(n)) == c

    # In each column exactly c coins must be placed.
    for j in range(n):
        model += mip.xsum(x[i][j] for i in range(n)) == c

    # The sum of the quadratic horizontal distance from the main diagonal of all cells containing a coin.
    model += z == mip.xsum((j - i) ** 2 * x[i][j] for i in range(n) for j in range(n))

    model.objective = z
    return model, {"x": x, "z": z}
