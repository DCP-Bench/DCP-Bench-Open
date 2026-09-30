# Aircraft landing with a fixed landing order: give every aircraft a landing
# time in its window so that later aircraft keep the required separation after
# earlier ones, at the least total penalty for landing early or late.
using JuMP

function build(instance)
    earliest = instance["earliest_landing"]
    latest = instance["latest_landing"]
    target = instance["target_landing"]
    penalty_after = instance["penalty_after"]     # per time unit after the target
    penalty_before = instance["penalty_before"]   # per time unit before the target
    separation = instance["separation_time"]      # separation[i][j]: least gap from i to j
    n = length(earliest)
    horizon = maximum(latest)
    model = Model()
    # each aircraft lands inside its window
    @variable(model, earliest[i] <= landing[i = 1:n] <= latest[i], Int)
    @variable(model, 0 <= earliness[1:n] <= horizon, Int)
    @variable(model, 0 <= lateness[1:n] <= horizon, Int)
    # the deviation from the target, split into earliness and lateness
    @constraint(model, [i = 1:n], landing[i] - target[i] == lateness[i] - earliness[i])
    # aircraft j lands after aircraft i, at least separation[i][j] later
    @constraint(model, [i = 1:n, j = i+1:n], landing[j] - landing[i] >= separation[i][j])
    # the total penalty, a declared output
    ub = horizon * (sum(penalty_before) + sum(penalty_after))
    @variable(model, 0 <= total_penalty <= ub, Int)
    @constraint(model, total_penalty ==
                sum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i] for i in 1:n))
    @objective(model, Min, total_penalty)
    return model, Dict("landing_times" => landing, "total_penalty" => total_penalty)
end
