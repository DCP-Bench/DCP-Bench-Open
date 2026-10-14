# Facility location: which of the candidate warehouses to open and how many
# units each ships to each region, meeting every region's demand at the least
# fixed plus shipping cost, under three rules about which warehouses may be open.
using JuMP

function build(instance)
    names = instance["warehouse_s"]              # warehouse cities
    fixed_costs = instance["fixed_costs"]        # weekly fixed cost of each warehouse
    max_shipping = instance["max_shipping"]      # most units a warehouse sends per week
    demands = instance["demands"]                # weekly demand of each region
    shipping_costs = instance["shipping_costs"]  # cost per unit from warehouse i to region j
    nw = length(names)
    nr = length(demands)
    city(name) = findfirst(==(name), names)
    new_york, los_angeles, atlanta = city("New York"), city("Los Angeles"), city("Atlanta")
    model = Model()
    @variable(model, open_warehouse[1:nw], Bin)
    @variable(model, 0 <= ships[1:nw, 1:nr] <= max_shipping, Int)
    # a warehouse sends at most max_shipping units, and nothing when closed
    @constraint(model, [i = 1:nw], sum(ships[i, :]) <= max_shipping * open_warehouse[i])
    # every region receives at least its demand
    @constraint(model, [j = 1:nr], sum(ships[:, j]) >= demands[j])
    # 1. if the New York warehouse is open, the Los Angeles one is open too
    @constraint(model, open_warehouse[new_york] <= open_warehouse[los_angeles])
    # 2. at most three warehouses are open
    @constraint(model, sum(open_warehouse) <= 3)
    # 3. the Atlanta or the Los Angeles warehouse (or both) is open
    @constraint(model, open_warehouse[atlanta] + open_warehouse[los_angeles] >= 1)
    # the total cost, a declared output
    ub = sum(fixed_costs) + max_shipping * sum(maximum(row) for row in shipping_costs)
    @variable(model, 0 <= total_cost <= ub, Int)
    @constraint(model, total_cost == sum(fixed_costs[i] * open_warehouse[i] for i in 1:nw) +
                                     sum(shipping_costs[i][j] * ships[i, j] for i in 1:nw, j in 1:nr))
    @objective(model, Min, total_cost)
    return model, Dict("total_cost" => total_cost, "open_warehouse" => open_warehouse, "ships" => ships)
end
