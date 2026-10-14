# Warehouse location: which candidate warehouses to open and which open
# warehouse supplies each store, so that no warehouse serves more stores than
# its capacity, at the least maintenance plus supply cost.
using JuMP

function build(instance)
    nw = instance["n_suppliers"]              # candidate warehouses
    ns = instance["n_stores"]
    building_cost = instance["building_cost"] # maintenance of one open warehouse
    capacity = instance["capacity"]           # most stores a warehouse can supply
    cost = instance["cost_matrix"]            # cost[store][warehouse]
    model = Model()
    # serves[s, w] = 1 when warehouse w supplies store s
    @variable(model, serves[1:ns, 1:nw], Bin)
    @variable(model, open_warehouses[1:nw], Bin)
    # the supplier of each store, 0-based, a declared output
    @variable(model, 0 <= supplier[1:ns] <= nw - 1, Int)
    @constraint(model, [s = 1:ns], sum(serves[s, :]) == 1)
    @constraint(model, [s = 1:ns], supplier[s] == sum((w - 1) * serves[s, w] for w in 1:nw))
    # a warehouse supplies at most its capacity
    @constraint(model, [w = 1:nw], sum(serves[:, w]) <= capacity[w])
    # a warehouse is open exactly when it supplies some store
    @constraint(model, [s = 1:ns, w = 1:nw], serves[s, w] <= open_warehouses[w])
    @constraint(model, [w = 1:nw], open_warehouses[w] <= sum(serves[:, w]))
    # the total cost, a declared output
    ub = sum(maximum(row) for row in cost) + nw * building_cost
    @variable(model, 0 <= total_cost <= ub, Int)
    @constraint(model, total_cost == sum(cost[s][w] * serves[s, w] for s in 1:ns, w in 1:nw) +
                                     building_cost * sum(open_warehouses))
    @objective(model, Min, total_cost)
    return model, Dict("total_cost" => total_cost, "open_warehouses" => open_warehouses,
                       "supplier_assignment" => supplier)
end
