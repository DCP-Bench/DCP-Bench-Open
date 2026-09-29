% Aircraft assignment: choose how many aircraft of each type fly each route so
% every route's passenger demand is met, no type is used beyond its fleet, and
% the total operating cost is minimal.
include "globals.mzn";

array[int] of int: availability;  % aircraft available per type
array[int] of int: demand;        % passengers to carry per route
array[int, int] of int: capabilities;  % passengers a type carries on a route
array[int, int] of int: costs;         % cost of one aircraft of a type on a route

set of int: Types = index_set(availability);
set of int: Routes = index_set(demand);

% allocation[i, j] = number of aircraft of type i assigned to route j; a type
% never needs more aircraft on one route than its whole fleet
array[Types, Routes] of var 0..max(availability): allocation;

% a type cannot be assigned more aircraft than are available
constraint forall(i in Types) (sum(j in Routes) (allocation[i, j]) <= availability[i]);

% the aircraft on each route together carry at least the route's demand
constraint forall(j in Routes) (sum(i in Types) (capabilities[i, j] * allocation[i, j]) >= demand[j]);

% minimise the total operating cost of the assignment
var int: objective = sum(i in Types, j in Routes) (costs[i, j] * allocation[i, j]);
solve minimize objective;

output ["{\"allocation\": [",
        join(", ", ["[" ++ join(", ", [show(allocation[i, j]) | j in Routes]) ++ "]" | i in Types]),
        "]}"];
