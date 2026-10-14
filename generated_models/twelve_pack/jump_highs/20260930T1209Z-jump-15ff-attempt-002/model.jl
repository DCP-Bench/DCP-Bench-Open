# Twelve pack: combine packs of the given sizes to reach at least the target
# number of items, as close to it as possible.
using JuMP

function build(instance)
    target = instance["target"]
    packs = instance["packs"]
    n = length(packs)
    max_count = 2 * target        # as the reference bounds the counts
    model = Model()
    @variable(model, 0 <= counts[1:n] <= max_count, Int)
    @variable(model, 0 <= total <= max_count * n, Int)
    @constraint(model, total == sum(packs[i] * counts[i] for i in 1:n))
    @constraint(model, total >= target)
    @objective(model, Min, total)
    return model, Dict("counts" => counts)
end
