# Aircraft assignment: how many aircraft of each type fly each route so that
# every route's passenger demand is met, no type is used beyond its fleet, and
# the operating cost is as small as possible.
using JuMP

function build(instance)
    availability = instance["availability"]   # aircraft available of each type
    demand = instance["demand"]               # passengers to carry on each route
    capabilities = instance["capabilities"]   # passengers a type carries on a route
    costs = instance["costs"]                 # cost of one aircraft of a type on a route
    nt = length(availability)
    nr = length(demand)
    model = Model()
    @variable(model, 0 <= allocation[1:nt, 1:nr] <= maximum(availability), Int)
    # a type is not used beyond its fleet
    @constraint(model, [i = 1:nt], sum(allocation[i, j] for j in 1:nr) <= availability[i])
    # every route carries at least its demand
    @constraint(model, [j = 1:nr], sum(capabilities[i][j] * allocation[i, j] for i in 1:nt) >= demand[j])
    @objective(model, Min, sum(costs[i][j] * allocation[i, j] for i in 1:nt, j in 1:nr))
    return model, Dict("allocation" => allocation)
end
