# Multi-commodity transportation: ship every product from the origins to the
# destinations, within the supplies and the per-route limits and meeting the
# demands, at the least total cost.
using JuMP

function build(instance)
    supply = instance["supply"]   # supply[i][p]
    demand = instance["demand"]   # demand[j][p]
    limit = instance["limit"]     # limit[i][j], over all products
    cost = instance["cost"]       # cost[i][j][p] per unit
    no = length(supply)
    nd = length(demand)
    np = length(supply[1])
    max_supply = maximum(maximum(row) for row in supply)
    model = Model()
    # x[i, j, p] = units of product p from origin i to destination j
    @variable(model, 0 <= x[1:no, 1:nd, 1:np] <= max_supply, Int)
    @constraint(model, [i = 1:no, p = 1:np], sum(x[i, j, p] for j in 1:nd) <= supply[i][p])
    @constraint(model, [j = 1:nd, p = 1:np], sum(x[i, j, p] for i in 1:no) >= demand[j][p])
    @constraint(model, [i = 1:no, j = 1:nd], sum(x[i, j, p] for p in 1:np) <= limit[i][j])
    # the total cost, the declared output, bounded as the reference bounds it
    ub = sum(sum(row) for row in supply) * maximum(maximum(maximum(r) for r in m) for m in cost)
    @variable(model, 0 <= total_cost <= ub, Int)
    @constraint(model, total_cost == sum(cost[i][j][p] * x[i, j, p] for i in 1:no, j in 1:nd, p in 1:np))
    @objective(model, Min, total_cost)
    return model, Dict("total_cost" => total_cost)
end
