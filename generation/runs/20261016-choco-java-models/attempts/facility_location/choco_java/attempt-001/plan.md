Problem: choose warehouses to open (four cities) and shipments from each open warehouse to each region, minimising fixed plus shipping cost.

- each warehouse is open (1) or closed (0) -> BoolVar open[i]
- region j's demand is met exactly by the shipments into it -> sum_i ships[i][j] = demands[j]
- a warehouse ships at most max_shipping, and nothing if closed -> sum_j ships[i][j] - max_shipping * open[i] <= 0 (scalar)
- ships[i][j] in 0..demands[j] (a shipment never exceeds the demand it serves)
- restriction 1: if New York is opened, Los Angeles must be opened -> open[NY] <= open[LA]
- restriction 2: no more than three warehouses operational -> sum open <= 3
- restriction 3: Atlanta or Los Angeles must be opened -> open[ATL] + open[LA] >= 1
- objective: total_cost = sum fixed_costs[i] * open[i] + sum shipping_costs[i][j] * ships[i][j] -> scalar, minimise
- The city indices come from the instance field warehouse_s (looked up by name), and the number of regions from demands (instances have 2 to 5 regions); the description's [4][3] shape is only the example.
- Outputs: open_warehouse (BoolVar[4]), ships (IntVar[4][R]), total_cost (IntVar).
