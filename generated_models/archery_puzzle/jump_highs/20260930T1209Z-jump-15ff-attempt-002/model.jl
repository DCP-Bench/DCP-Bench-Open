# Archery puzzle: how close can the archer come to the target score, hitting
# each target as often as she likes?
using JuMP

function build(instance)
    targets = instance["targets"]
    target_score = instance["target_score"]
    n = length(targets)
    model = Model()
    # hits[i] = the arrows that hit target i
    @variable(model, 0 <= hits[1:n] <= target_score, Int)
    @variable(model, 0 <= score <= 2 * target_score, Int)
    @constraint(model, score == sum(targets[i] * hits[i] for i in 1:n))
    # the distance from the target score; minimising it makes it exact
    @variable(model, 0 <= deviation <= 2 * target_score, Int)
    @constraint(model, deviation >= target_score - score)
    @constraint(model, deviation >= score - target_score)
    @objective(model, Min, deviation)
    return model, Dict("hits" => hits)
end
