# Media selection: choose advertising media so that every target audience is
# reached by at least one of them, at the least total cost.
using JuMP

function build(instance)
    incidence = instance["incidence_matrix"]   # incidence[t][m] = 1 when medium m reaches t
    costs = instance["media_costs"]
    na = length(instance["target_audiences"])
    nm = length(instance["advertising_media"])
    model = Model()
    @variable(model, selected[1:nm], Bin)
    # every audience is reached
    @constraint(model, [t = 1:na], sum(incidence[t][m] * selected[m] for m in 1:nm) >= 1)
    # the total cost, a declared output
    @variable(model, 0 <= total <= sum(costs), Int)
    @constraint(model, total == sum(costs[m] * selected[m] for m in 1:nm))
    @objective(model, Min, total)
    return model, Dict("is_selected" => selected, "min_total_cost" => total)
end
