from pycsp3 import *

# the warehouses are the suppliers, the stores are the customers of the instance
n_stores = data.n_stores
n_suppliers = data.n_suppliers
costs = data.cost_matrix

# open_warehouses[w] is 1 when warehouse w is open
open_warehouses = VarArray(size=n_suppliers, dom={0, 1})
# supplier_assignment[s] is the warehouse that supplies store s
supplier_assignment = VarArray(size=n_stores, dom=range(n_suppliers))
# supply_cost[s] is the cost of supplying store s from its warehouse
supply_cost = VarArray(size=n_stores, dom=sorted({c for row in costs for c in row}))
# total cost: maintenance of the open warehouses plus the supply costs
total_cost = Var(dom=range(0, sum(max(row) for row in costs) + data.building_cost * n_suppliers + 1))

satisfy(
    # each store is supplied by exactly one warehouse, and that warehouse is open
    [open_warehouses[supplier_assignment[s]] == 1 for s in range(n_stores)],
    # the number of stores a warehouse supplies is within its capacity
    [Count(supplier_assignment, value=w) <= data.capacity[w] for w in range(n_suppliers)],
    # the supply cost of a store depends on the store and the warehouse it is assigned to
    [Table(scope=[supplier_assignment[s], supply_cost[s]],
           supports=[(w, costs[s][w]) for w in range(n_suppliers)]) for s in range(n_stores)],
    # the total cost is the maintenance cost of the open warehouses plus the supply costs
    total_cost == Sum(data.building_cost * open_warehouses[w] for w in range(n_suppliers))
    + Sum(supply_cost[s] for s in range(n_stores)),
)

# minimise the total cost
minimize(total_cost)
