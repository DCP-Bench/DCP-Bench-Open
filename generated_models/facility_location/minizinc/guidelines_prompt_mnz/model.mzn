
% Warehouse location and shipping model

% Include standard global constraints library
include "globals.mzn";

% Input data
int: num_warehouses = 4;
int: num_regions = 3;
array[1..num_warehouses] of string: warehouse_s = ["New York", "Los Angeles", "Chicago", "Atlanta"];
array[1..num_warehouses] of int: fixed_costs = [400, 500, 300, 150];
int: max_shipping = 100;
array[1..num_regions] of int: demands = [80, 70, 40];
array[1..num_warehouses, 1..num_regions] of int: shipping_costs = 
    array2d(1..num_warehouses, 1..num_regions, 
        [20,40,50,  % New York
         48,15,26,  % Los Angeles
         26,35,18,  % Chicago
         24,50,35]  % Atlanta
    );

% Decision variables
% 1 if warehouse w is opened, 0 otherwise
array[1..num_warehouses] of var 0..1: open_warehouse;
% units shipped from warehouse w to region r
array[1..num_warehouses, 1..num_regions] of var 0..max_shipping: ships;

% Total cost: fixed + shipping
var int: total_cost = 
    sum(w in 1..num_warehouses)(fixed_costs[w] * open_warehouse[w])
  + sum(w in 1..num_warehouses, r in 1..num_regions)(shipping_costs[w,r] * ships[w,r]);

% Constraints

% 1. If New York (1) is opened then Los Angeles (2) must be opened
constraint open_warehouse[1] <= open_warehouse[2];

% 2. At most three warehouses can be operational
constraint sum(w in 1..num_warehouses)(open_warehouse[w]) <= 3;

% 3. Either Atlanta (4) or Los Angeles (2) must be opened
constraint open_warehouse[2] + open_warehouse[4] >= 1;

% 4. Capacity limit per warehouse
constraint forall(w in 1..num_warehouses) (
    sum(r in 1..num_regions)(ships[w,r]) <= max_shipping * open_warehouse[w]
);

% 5. Demand fulfillment for each region
constraint forall(r in 1..num_regions) (
    sum(w in 1..num_warehouses)(ships[w,r]) >= demands[r]
);

% Solve: minimize total cost
solve minimize total_cost;

% Output in JSON format
output [
    "{",
    "\"total_cost\": " ++ show(total_cost) ++ ",",
    "\"open_warehouse\": [" ++
        join(",", [show(open_warehouse[w]) | w in 1..num_warehouses]) ++
    "],",
    "\"ships\": [" ++
        join(",", [
            "[" ++ join(",", [show(ships[w,r]) | r in 1..num_regions]) ++ "]"
            | w in 1..num_warehouses
        ]) ++
    "]",
    "}"
];
