# Plan: csplib_034_warehouse_location

- "decide which warehouses to open" -> open[j] = Bool per warehouse j (output open_warehouses, [n_suppliers]bool)
- "Each store must be supplied by exactly one open warehouse" -> one-hot assign[i][j] per store i, sum_j assign[i][j] == 1; assign[i][j] -> open[j]
- "a capacity limiting the number of stores it can supply" -> per warehouse j, sum_i assign[i][j] <= capacity[j]
- "supply cost that varies depending on the store and warehouse" -> sum_{i,j} cost_matrix[i][j] * assign[i][j]
- "fixed maintenance cost for all opened warehouses" -> sum_j building_cost * open[j]
- "supplied by warehouse" output supplier_assignment[i] = sum_j j * assign[i][j] (0-based), int list of n_stores
- objective "minimize the total cost" -> minimise total_cost = maintenance + supply (same expression as output total_cost)
