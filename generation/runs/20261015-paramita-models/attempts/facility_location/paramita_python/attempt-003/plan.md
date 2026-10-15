Warehouse i is opened (open_warehouse[i]) -> Bool open_i
Ships from warehouse i to region j (ships[i][j], units) -> integer 0..min(max_shipping, demand_j), unary bits ship_i_j_ge_k with If(ge_{k+1}, ge_k)
If the New York warehouse is opened, then the Los Angeles warehouse must also be opened -> If(open_NY, open_LA)
No more than three warehouses can be operational in any given week -> sum(open) <= 3
Either the Atlanta or the Los Angeles warehouse must be opened -> Or([open_ATL, open_LA])
A warehouse ships at most max_shipping units in total, and nothing when closed (ships[i][j] = 0 for non-opened) -> sum_j ships[i][j] <= max_shipping * open_i
Each region's demand is met exactly by the warehouses -> sum_i ships[i][j] == demands[j]
Total cost = fixed costs of opened warehouses + shipping costs -> objective sum(fixed_i * open_i) + sum(shipping_costs[i][j] * ships[i][j]), minimise
