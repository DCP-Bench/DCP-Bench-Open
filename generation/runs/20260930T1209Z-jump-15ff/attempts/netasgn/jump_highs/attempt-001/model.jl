# Network assignment: hours from people to projects, every person working all
# their hours and every project getting all its hours, within the per-pair
# limits, at the least total cost.
using JuMP

function build(instance)
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    np = length(supply)
    nj = length(demand)
    model = Model()
    # assign[i, j] = hours of person i on project j: 0..10 as the reference
    # bounds it, and within the limit of the pair
    @variable(model, 0 <= assign[i = 1:np, j = 1:nj] <= min(10, limit[i][j]), Int)
    @constraint(model, [i = 1:np], sum(assign[i, :]) == supply[i])
    @constraint(model, [j = 1:nj], sum(assign[:, j]) == demand[j])
    # the total cost, a declared output
    ub = sum(10 * cost[i][j] for i in 1:np, j in 1:nj)
    @variable(model, 0 <= total_cost <= ub, Int)
    @constraint(model, total_cost == sum(cost[i][j] * assign[i, j] for i in 1:np, j in 1:nj))
    @objective(model, Min, total_cost)
    return model, Dict("assign" => assign, "total_cost" => total_cost)
end
