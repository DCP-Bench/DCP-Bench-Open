# Futoshiki: fill an n x n grid with 1..n so that every row and every column
# holds each number once, the given numbers stay, and each listed pair of cells
# satisfies its "less than" sign.
using JuMP

function build(instance)
    values = instance["values"]   # given numbers, 0 where a cell is empty
    lt = instance["lt"]           # [i1, j1, i2, j2]: cell (i1, j1) < cell (i2, j2), 1-based
    n = length(values)
    model = Model()
    @variable(model, has[1:n, 1:n, 1:n], Bin)
    @constraint(model, [i = 1:n, j = 1:n], sum(has[i, j, :]) == 1)
    @constraint(model, [i = 1:n, v = 1:n], sum(has[i, :, v]) == 1)
    @constraint(model, [j = 1:n, v = 1:n], sum(has[:, j, v]) == 1)
    @variable(model, 1 <= grid[1:n, 1:n] <= n, Int)
    @constraint(model, [i = 1:n, j = 1:n], grid[i, j] == sum(v * has[i, j, v] for v in 1:n))
    # the given numbers stay
    for i in 1:n, j in 1:n
        values[i][j] > 0 && fix(has[i, j, values[i][j]], 1; force = true)
    end
    # every inequality sign holds
    for s in lt
        @constraint(model, grid[s[1], s[2]] + 1 <= grid[s[3], s[4]])
    end
    return model, Dict("grid" => grid)
end
