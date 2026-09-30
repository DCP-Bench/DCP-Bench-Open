# Broken weights: a weight of m pounds broke into n whole-pound pieces with
# which every weight from 1 to m can be weighed on a balance scale, each piece
# on the object's pan, on the other pan, or off.
using JuMP

function build(instance)
    m = instance["m"]
    n = instance["n"]
    model = Model()
    @variable(model, 1 <= weights[1:n] <= m, Int)
    @constraint(model, sum(weights) == m)
    # For each weight t, a piece j goes on one pan (on[t, j, 1]), the other
    # (on[t, j, 2]) or neither; part = weights[j] * on, linearised with weights <= m.
    @variable(model, on[1:m, 1:n, 1:2], Bin)
    @constraint(model, [t = 1:m, j = 1:n], on[t, j, 1] + on[t, j, 2] <= 1)
    @variable(model, 0 <= part[1:m, 1:n, 1:2] <= m, Int)
    @constraint(model, [t = 1:m, j = 1:n, k = 1:2], part[t, j, k] <= m * on[t, j, k])
    @constraint(model, [t = 1:m, j = 1:n, k = 1:2], part[t, j, k] <= weights[j])
    @constraint(model, [t = 1:m, j = 1:n, k = 1:2], part[t, j, k] >= weights[j] - m * (1 - on[t, j, k]))
    # every weight t can be weighed
    @constraint(model, [t = 1:m], sum(part[t, j, 1] - part[t, j, 2] for j in 1:n) == t)
    return model, Dict("weights" => weights)
end
