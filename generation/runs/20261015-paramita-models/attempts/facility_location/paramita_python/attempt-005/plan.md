Open warehouses in four cities (New York, Los Angeles, Chicago, Atlanta) -> open[i] Bool per city, city index looked up from instance warehouse_s
If the New York warehouse is opened, then the Los Angeles warehouse must also be opened -> If(open[NY], open[LA])
No more than three warehouses can be operational -> sum(open) <= 3
Either the Atlanta or the Los Angeles warehouse must be opened -> Or([open[ATL], open[LA]])
Meet regional demands (per region j: shipments from all warehouses equal demand) -> ships[i][j] binary (nbits = max_shipping.bit_length(), weights 2^k); sum_i ships[i][j] == demands[j]
Warehouse i ships at most max_shipping units, and only when open -> sum_j ships[i][j] <= max_shipping * open[i]
Objective: minimise fixed opening costs plus shipping costs -> sum fixed_costs[i]*open[i] + sum shipping_costs[i][j]*ships[i][j] (binary bit weights)
