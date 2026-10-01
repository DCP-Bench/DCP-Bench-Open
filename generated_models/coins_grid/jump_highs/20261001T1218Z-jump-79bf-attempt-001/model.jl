# Coins on a grid: place coins on an n x n grid, at most one per cell, with exactly
# c coins in every row and in every column, so that the sum over all coins of the
# squared horizontal distance to the main diagonal (the coin's row index minus
# its column index, squared) is as small as possible.
using JuMP

function build(instance)
    n = instance["n"]   # grid size
    c = instance["c"]   # coins in each row and each column
    model = Model()

    # x[i, j] = 1 when cell (i, j) holds a coin (at most one coin per cell)
    @variable(model, x[1:n, 1:n], Bin)

    # every row holds exactly c coins
    @constraint(model, [i = 1:n], sum(x[i, :]) == c)
    # every column holds exactly c coins
    @constraint(model, [j = 1:n], sum(x[:, j]) == c)

    # z = the sum of the squared distances of the coins to the main diagonal, a declared
    # output; the bound is every cell with the largest distance (n - 1)^2
    @variable(model, 0 <= z <= n * n * (n - 1)^2, Int)
    @constraint(model, z == sum((i - j)^2 * x[i, j] for i in 1:n, j in 1:n))

    @objective(model, Min, z)
    return model, Dict("x" => x, "z" => z)
end
