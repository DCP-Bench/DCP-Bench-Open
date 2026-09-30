# Pythagorean triplet: natural numbers a, b, c with a^2 + b^2 = c^2 and
# a + b + c = 1000.
using JuMP

function build(instance)
    # The puzzle has no data.
    values = 1:500
    model = Model()
    # is[k, v] = 1 when the k-th number (a, b, c) is v
    @variable(model, is[1:3, values], Bin)
    @constraint(model, [k = 1:3], sum(is[k, :]) == 1)
    @variable(model, 1 <= abc[1:3] <= 500, Int)
    @constraint(model, [k = 1:3], abc[k] == sum(v * is[k, v] for v in values))
    @constraint(model, sum(abc) == 1000)
    @constraint(model, sum(v^2 * is[1, v] for v in values) + sum(v^2 * is[2, v] for v in values) ==
                       sum(v^2 * is[3, v] for v in values))
    return model, Dict("a" => abc[1], "b" => abc[2], "c" => abc[3])
end
