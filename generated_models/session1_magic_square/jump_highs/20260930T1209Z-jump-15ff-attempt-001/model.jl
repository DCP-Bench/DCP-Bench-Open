# Magic square: fill an n x n grid with the different integers 1..n^2 so that
# every row, every column and both diagonals add up to n(n^2 + 1)/2.
using JuMP

function build(instance)
    n = instance["n"]
    total = div(n * (n^2 + 1), 2)
    model = Model()
    @variable(model, 1 <= square[1:n, 1:n] <= n^2, Int)
    # all numbers are different
    @constraint(model, vec(square) in MOI.AllDifferent(n^2))
    @constraint(model, [i = 1:n], sum(square[i, :]) == total)
    @constraint(model, [j = 1:n], sum(square[:, j]) == total)
    @constraint(model, sum(square[i, i] for i in 1:n) == total)
    @constraint(model, sum(square[i, n + 1 - i] for i in 1:n) == total)
    return model, Dict("square" => square)
end
