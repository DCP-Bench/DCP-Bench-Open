% Facility location: decide which of four candidate warehouses to open and how
% many units each ships to each region, meeting every region's demand at the
% least total cost (fixed cost of the open warehouses plus shipping cost),
% subject to three rules about which warehouses may be open together.
include "globals.mzn";

array[int] of string: warehouse_s;    % warehouse cities
array[int] of int: fixed_costs;       % weekly fixed cost of each warehouse
int: max_shipping;                    % most units one warehouse can send per week
array[int] of int: demands;           % weekly demand of each region
array[int, int] of int: shipping_costs;  % cost per unit from warehouse i to region j

set of int: Warehouses = index_set(warehouse_s);
set of int: Regions = index_set(demands);

% the position of a city in the list of warehouses
function int: position_of(string: city) = min([i | i in Warehouses where warehouse_s[i] = city]);
int: new_york = position_of("New York");
int: los_angeles = position_of("Los Angeles");
int: atlanta = position_of("Atlanta");

% open_warehouse[i] is true when warehouse i is open
array[Warehouses] of var bool: open_warehouse;
% ships[i, j] = units sent from warehouse i to region j (0 for a closed warehouse)
array[Warehouses, Regions] of var 0..max_shipping: ships;

% a warehouse sends at most max_shipping units, and nothing when it is closed
constraint forall(i in Warehouses) (sum(j in Regions) (ships[i, j]) <= max_shipping * bool2int(open_warehouse[i]));

% every region receives at least its demand
constraint forall(j in Regions) (sum(i in Warehouses) (ships[i, j]) >= demands[j]);

% 1. if the New York warehouse is open, the Los Angeles one must be open too
constraint open_warehouse[new_york] -> open_warehouse[los_angeles];
% 2. at most three warehouses are open
constraint sum(i in Warehouses) (bool2int(open_warehouse[i])) <= 3;
% 3. the Atlanta or the Los Angeles warehouse (or both) must be open
constraint open_warehouse[atlanta] \/ open_warehouse[los_angeles];

% total cost = fixed costs of the open warehouses + cost of everything shipped
var 0..10000: total_cost = sum(i in Warehouses) (fixed_costs[i] * bool2int(open_warehouse[i]))
                           + sum(i in Warehouses, j in Regions) (shipping_costs[i, j] * ships[i, j]);
var int: objective = total_cost;
solve minimize objective;

output ["{\"total_cost\": ", show(total_cost),
        ", \"open_warehouse\": [", join(", ", [show(open_warehouse[i]) | i in Warehouses]),
        "], \"ships\": [",
        join(", ", ["[" ++ join(", ", [show(ships[i, j]) | j in Regions]) ++ "]" | i in Warehouses]), "]}"];
