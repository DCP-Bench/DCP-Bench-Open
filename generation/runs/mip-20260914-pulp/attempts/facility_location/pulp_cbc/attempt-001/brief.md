# facility_location
Instance: `warehouse_s`, `fixed_costs`, `max_shipping`, `demands`,
`shipping_costs`. Outputs: `total_cost`, `open_warehouse` (0/1 per warehouse),
`ships` (warehouse x region matrix, 0..max_shipping).
Minimize fixed plus shipping cost, meeting each region's demand, with three
side conditions the reference states positionally: warehouse 0 open implies
warehouse 1 open, at most three open, and warehouse 3 or warehouse 1 open.
`total_cost` is bounded 0..10000 as in the reference.
