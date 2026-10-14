# Heterosquare: an n x n square of the different numbers 1..n^2 whose row sums,
# column sums and two diagonal sums are all different.
using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    @variable(model, 1 <= x[1:n, 1:n] <= n^2, Int)
    @constraint(model, vec(x) in MOI.AllDifferent(n^2))
    @variable(model, 1 <= sums[1:2n+2] <= n^3, Int)
    @constraint(model, [i = 1:n], sums[i] == sum(x[i, :]))
    @constraint(model, [j = 1:n], sums[n + j] == sum(x[:, j]))
    @constraint(model, sums[2n + 1] == sum(x[i, i] for i in 1:n))
    @constraint(model, sums[2n + 2] == sum(x[i, n + 1 - i] for i in 1:n))
    # all the sums are different
    @constraint(model, sums in MOI.AllDifferent(2n + 2))
    return model, Dict("x" => x)
end
