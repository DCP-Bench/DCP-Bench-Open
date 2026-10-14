# Cutting stock: how many times to cut each pattern so that every width's orders
# are met with as few raw rolls as possible.
using JuMP

function build(instance)
    orders = instance["orders"]
    patterns = instance["num_rolls_width"]   # patterns[p][w] = pieces of width w in pattern p
    np = instance["num_patterns"]
    nw = length(orders)
    model = Model()
    # each pattern is used 0..100 times, as the reference bounds it
    @variable(model, 0 <= used[1:np] <= 100, Int)
    @constraint(model, [w = 1:nw], sum(patterns[p][w] * used[p] for p in 1:np) >= orders[w])
    @variable(model, 0 <= rolls <= 100 * np, Int)
    @constraint(model, rolls == sum(used))
    @objective(model, Min, rolls)
    return model, Dict("patterns_used" => used, "min_rolls_cut" => rolls)
end
