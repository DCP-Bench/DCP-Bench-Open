# fixed_charge
Instance carries the machines, products, resources, `renting_cost`, `capacity`,
`max_production`, `product` (profit and machine per product) and `use`
(resource use per product). Output: `z` only, bounded 0..10000.
Maximize profit minus renting cost, within each resource's capacity, producing
only on a rented machine.
