# Production planning: quantities x[j] up to u[j] such that the sum of
# x[j] / a[j] stays within b and the profit sum of c[j] * x[j] is as large as
# possible.
using JuMP

function build(instance)
    a = instance["a"]
    b = instance["b"]
    c = instance["c"]
    u = instance["u"]
    n = length(a)
    # the least common multiple of the a[j], to clear the divisions
    m = lcm(Int.(a))
    model = Model()
    @variable(model, 0 <= x[j = 1:n] <= u[j], Int)
    # sum of x[j] / a[j] <= b, multiplied through by the lcm
    @constraint(model, sum(div(m, a[j]) * x[j] for j in 1:n) <= b * m)
    # the profit, a declared output
    @variable(model, 0 <= profit <= sum(c[j] * u[j] for j in 1:n), Int)
    @constraint(model, profit == sum(c[j] * x[j] for j in 1:n))
    @objective(model, Max, profit)
    return model, Dict("x" => x, "total_profit" => profit)
end
