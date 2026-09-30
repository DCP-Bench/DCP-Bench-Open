# Four different numbers from 1 to 100 with a^2 + b^2 = c^2 + d^2.
using JuMP

function build(instance)
    # The puzzle has no data.
    values = 1:100
    model = Model()
    @variable(model, is[1:4, values], Bin)
    @constraint(model, [k = 1:4], sum(is[k, :]) == 1)
    @constraint(model, [v = values], sum(is[:, v]) <= 1)   # all different
    @variable(model, 1 <= x[1:4] <= 100, Int)
    @constraint(model, [k = 1:4], x[k] == sum(v * is[k, v] for v in values))
    sq = [sum(v^2 * is[k, v] for v in values) for k in 1:4]
    @constraint(model, sq[1] + sq[2] == sq[3] + sq[4])
    return model, Dict("a" => x[1], "b" => x[2], "c" => x[3], "d" => x[4])
end
