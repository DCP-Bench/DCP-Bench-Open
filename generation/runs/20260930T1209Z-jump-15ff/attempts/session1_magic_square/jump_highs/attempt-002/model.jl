# Magic square: fill an n x n grid with the different integers 1..n^2 so that
# every row, every column and both diagonals add up to n(n^2 + 1)/2.
# This version states the numbers with one binary per cell and value, which
# gives HiGHS a tighter relaxation than the bridged all-different.
using JuMP

function build(instance)
    n = instance["n"]
    total = div(n * (n^2 + 1), 2)
    values = 1:n^2
    model = Model()
    # has[i, j, v] = 1 when cell (i, j) holds v; every cell one value, every value once
    @variable(model, has[1:n, 1:n, values], Bin)
    @constraint(model, [i = 1:n, j = 1:n], sum(has[i, j, v] for v in values) == 1)
    @constraint(model, [v = values], sum(has[i, j, v] for i in 1:n, j in 1:n) == 1)
    @variable(model, 1 <= square[1:n, 1:n] <= n^2, Int)
    @constraint(model, [i = 1:n, j = 1:n], square[i, j] == sum(v * has[i, j, v] for v in values))
    @constraint(model, [i = 1:n], sum(square[i, :]) == total)
    @constraint(model, [j = 1:n], sum(square[:, j]) == total)
    @constraint(model, sum(square[i, i] for i in 1:n) == total)
    @constraint(model, sum(square[i, n + 1 - i] for i in 1:n) == total)
    return model, Dict("square" => square)
end
