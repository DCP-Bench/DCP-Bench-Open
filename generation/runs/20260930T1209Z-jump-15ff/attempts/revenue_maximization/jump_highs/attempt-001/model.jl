# Revenue maximisation: how many units of each flight package to sell, within
# the seats of the legs it uses and its demand, for the largest revenue.
using JuMP

function build(instance)
    seats = instance["available_seats"]   # seats on each flight leg
    demand = instance["demand"]           # estimated demand for each package
    revenue = instance["revenue"]
    delta = instance["delta"]             # delta[i][j] = 1 when package i uses leg j
    np = length(demand)
    nl = length(seats)
    model = Model()
    # no more than the demand of a package is sold
    @variable(model, 0 <= sell[i = 1:np] <= demand[i], Int)
    # the packages sold fit the seats of every leg
    @constraint(model, [j = 1:nl], sum(delta[i][j] * sell[i] for i in 1:np) <= seats[j])
    # the revenue, a declared output
    @variable(model, 0 <= total <= sum(revenue[i] * demand[i] for i in 1:np), Int)
    @constraint(model, total == sum(revenue[i] * sell[i] for i in 1:np))
    @objective(model, Max, total)
    return model, Dict("packages_to_sell" => sell, "max_revenue" => total)
end
