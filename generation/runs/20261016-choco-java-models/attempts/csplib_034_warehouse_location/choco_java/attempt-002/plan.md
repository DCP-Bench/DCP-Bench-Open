a company must decide which warehouses to open from a set of candidate locations -> open[w] BoolVar per warehouse, defined as load[w] > 0
Each store must be supplied by exactly one open warehouse -> assign[s] IntVar in 0..W-1 per store
a store can only be supplied by an open warehouse -> m.element(1, open, assign[s], 0)
each warehouse has a capacity limiting the number of stores it can supply -> m.globalCardinality(assign, 0..W-1, load, closed) with load[w] in 0..capacity[w]
there is an associated supply cost that varies depending on the store and warehouse -> supply[s] = m.element(cost_matrix[s], assign[s], 0)
the sum of the maintenance costs for all opened warehouses -> building_cost * open[w] summed
the supply costs for all stores -> sum of supply[s]
minimize the total cost -> total_cost = scalar sum, setObjective MINIMIZE
implied: the total is at least the sum over stores of the cheapest supply cost of that store (data-derived lower bound) -> m.arithm(total, ">=", lb)
search: branch on assign with dom/wdeg under last-conflict, Luby restarts (skill Search section, timeout repair)
Print total_cost, open_warehouses, supplier_assignment -> outputs total_cost, open, assign
