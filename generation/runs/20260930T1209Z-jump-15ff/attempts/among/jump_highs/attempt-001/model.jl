# Among: exactly m of the values in x lie in the set v; every value is 0..7.
using JuMP

function build(instance)
    n = instance["n"]
    m = instance["m"]
    v = instance["v"]
    model = Model()
    # is[i, k + 1] = 1 when x[i] = k
    @variable(model, is[1:n, 1:8], Bin)
    @constraint(model, [i = 1:n], sum(is[i, :]) == 1)
    @variable(model, 0 <= x[1:n] <= 7, Int)
    @constraint(model, [i = 1:n], x[i] == sum(k * is[i, k + 1] for k in 0:7))
    # as the reference counts: over the positions and the listed values, the
    # number of matches is m
    @constraint(model, sum(is[i, j + 1] for i in 1:n, j in v) == m)
    return model, Dict("x" => x)
end
