include "globals.mzn";

% Input data
int: num_warehouses = 4;
int: num_regions = 3;

array[1..num_warehouses] of string: warehouse_s = ["New York", "Los Angeles", "Chicago", "Atlanta"];
array[1..num_warehouses] of int: fixed_costs = [400, 500, 300, 150];
int: max_shipping = 100;
array[1..num_regions] of int: demands = [80, 70, 40];
array[1..num_warehouses, 1..num_regions] of int: shipping_costs = 
  [| 20, 40, 50
   | 48, 15, 26
   | 26, 35, 18
   | 24, 50, 35
  |];

% Decision variables
array[1..num_warehouses] of var bool: open_warehouse; % Whether each warehouse is open
array[1..num_warehouses, 1..num_regions] of var 0..max_shipping: ships; % Units shipped from warehouse to region

% Constraints

% 1. If New York warehouse is opened, then Los Angeles warehouse must also be opened.
constraint open_warehouse[1] -> open_warehouse[2];

% 2. No more than three warehouses can be operational in any given week.
constraint sum([bool2int(open_warehouse[i]) | i in 1..num_warehouses]) <= 3;

% 3. Either the Atlanta or the Los Angeles warehouse must be opened.
constraint open_warehouse[2] \/ open_warehouse[4];

% Shipments can only come from open warehouses
constraint forall(w in 1..num_warehouses, r in 1..num_regions) (
  ships[w,r] <= max_shipping * bool2int(open_warehouse[w])
);

% Warehouse capacity constraint: max units per warehouse per week
constraint forall(w in 1..num_warehouses) (
  sum([ships[w,r] | r in 1..num_regions]) <= max_shipping
);

% Demand satisfaction: sum of shipments to each region must meet demand
constraint forall(r in 1..num_regions) (
  sum([ships[w,r] | w in 1..num_warehouses]) >= demands[r]
);

% Objective: minimize total cost = sum of fixed costs for open warehouses + sum of shipping costs
var int: total_cost = 
  sum(w in 1..num_warehouses)(fixed_costs[w] * bool2int(open_warehouse[w])) +
  sum(w in 1..num_warehouses, r in 1..num_regions)(shipping_costs[w,r] * ships[w,r]);

solve minimize total_cost;

output [
  "{",
  "\"total_cost\": ", show(total_cost), ",",
  "\"open_warehouse\": ", show(open_warehouse), ",",
  "\"ships\": ", show(ships),
  "}"
];