In the Warehouse Location problem, a company must decide which warehouses to open
from a set of candidate locations to supply a set of stores. Each warehouse has a
fixed maintenance cost and a capacity limiting the number of stores it can supply.
Each store must be supplied by exactly one open warehouse, and there is an
associated supply cost that varies depending on the store and warehouse.

The objective is to minimize the total cost, which is the sum of the maintenance
costs for all opened warehouses and the supply costs for all stores.

Print the minimized total cost (total_cost), a binary list indicating which
warehouses are open (open_warehouses), and an integer list of `n_stores` elements - ranging from 0 to `n_suppliers-1` - showing the warehouse assigned
to each store (supplier_assignment).
