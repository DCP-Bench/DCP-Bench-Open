# Bales of hay: the bales were weighed in all combinations of two, and those
# weights, in numerical order, are given. Find the weight of each bale.
using JuMP

function build(instance)
    n = instance["n"]
    weights = instance["weights"]
    pairs = [(i, j) for i in 1:n-1 for j in i+1:n]
    np = length(pairs)
    model = Model()
    @variable(model, 0 <= bales[1:n] <= 50, Int)
    # which[k, p] = 1 when the k-th written weight belongs to pair p; every
    # written weight has its own pair
    @variable(model, which[1:length(weights), 1:np], Bin)
    @constraint(model, [k = 1:length(weights)], sum(which[k, :]) == 1)
    @constraint(model, [p = 1:np], sum(which[:, p]) <= 1)
    # a pair with a written weight weighs that much
    for k in 1:length(weights), p in 1:np
        i, j = pairs[p]
        @constraint(model, which[k, p] --> {bales[i] + bales[j] == weights[k]})
    end
    return model, Dict("bales" => bales)
end
