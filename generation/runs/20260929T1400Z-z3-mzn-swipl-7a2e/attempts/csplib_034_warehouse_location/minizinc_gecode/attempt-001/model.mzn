% Warehouse location: decide which candidate warehouses to open and which open
% warehouse supplies each store, so that no warehouse serves more stores than
% its capacity and the maintenance cost of the open warehouses plus the supply
% costs of all stores is minimal.
include "globals.mzn";

int: n_suppliers;  % candidate warehouses
int: n_stores;
int: building_cost;  % maintenance cost of one open warehouse
array[int] of int: capacity;  % most stores each warehouse can supply
array[int, int] of int: cost_matrix;  % cost_matrix[store, warehouse] = supply cost

% supplier_assignment[s] = the warehouse that supplies store s, numbered from 0
% as in the answer; warehouse w is column w + 1 of the cost matrix and of capacity
array[1..n_stores] of var 0..n_suppliers - 1: supplier_assignment;
% open_warehouses[w] is true when warehouse w (numbered from 1 here) is open
array[1..n_suppliers] of var bool: open_warehouses;

% a warehouse cannot supply more stores than its capacity
constraint forall(w in 1..n_suppliers) (
    sum(s in 1..n_stores) (bool2int(supplier_assignment[s] = w - 1)) <= capacity[w]);

% a warehouse is open exactly when it supplies at least one store; this also
% forbids supplying a store from a closed warehouse
constraint forall(w in 1..n_suppliers) (
    open_warehouses[w] <-> exists(s in 1..n_stores) (supplier_assignment[s] = w - 1));

% total cost = supply cost of every store + maintenance of the open warehouses
var int: total_cost = sum(s in 1..n_stores) (cost_matrix[s, supplier_assignment[s] + 1])
                      + building_cost * sum(w in 1..n_suppliers) (bool2int(open_warehouses[w]));
var int: objective = total_cost;
solve minimize objective;

output ["{\"total_cost\": ", show(total_cost),
        ", \"open_warehouses\": [", join(", ", [show(open_warehouses[w]) | w in 1..n_suppliers]),
        "], \"supplier_assignment\": [", join(", ", [show(supplier_assignment[s]) | s in 1..n_stores]), "]}"];
