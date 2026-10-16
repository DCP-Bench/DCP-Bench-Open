# Plan: warehouse location (csplib_034)

Warehouses W = n_suppliers, stores S = n_stores. open[w] bool; y[s][w] bool = store s supplied by w; supplier_assignment[s] = w (int).

- "decide which warehouses to open" -> BoolVarArray open(W) (output open_warehouses); branch on it first, BOOL_VAL_MIN
- "each store must be supplied by exactly one open warehouse" -> channel(*this, y[s][0..W-1], assign[s]) (one-hot: exactly one y true, equal to assign[s]) (map row: one-hot channel)
- "a store is supplied only by an open warehouse" -> rel(*this, y[s][w], IRT_LQ, open[w]) (map row: logic between conditions, bool implication)
- "each warehouse has a capacity limiting the number of stores it can supply" -> linear(*this, y column w, IRT_LQ, capacity[w]) (map row: how many are true)
- "supply cost varies depending on store and warehouse" -> linear(*this, IntArgs(cost flat s*W+w), y, IRT_EQ, supplyTotal) (map row: weighted count)
- "fixed maintenance cost for opened warehouses" -> linear(*this, IntArgs::create(W, building_cost, 0), open, IRT_EQ, fixedTotal) (map row: weighted count)
- "minimize the total cost" -> total = fixedTotal + supplyTotal via linear(parts, IRT_EQ, total); minimize(total)
- branching -> open first (BOOL_VAL_MIN), then assign (INT_VAR_SIZE_MIN, INT_VAL_MIN)
