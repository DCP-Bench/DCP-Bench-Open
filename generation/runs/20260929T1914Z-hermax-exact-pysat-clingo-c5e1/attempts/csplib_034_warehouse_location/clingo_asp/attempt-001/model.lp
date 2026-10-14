% Warehouse location: decide which candidate warehouses to open and which open
% warehouse supplies each store, so that no warehouse serves more stores than
% its capacity and the maintenance cost of the open warehouses plus the supply
% costs of all stores is minimal.
% capacity(W, C): warehouse W supplies at most C stores; cost_matrix(S, W, C): the cost of
% supplying store S from warehouse W; building_cost(B): the maintenance of an open warehouse.
warehouse(W) :- capacity(W,_).
store(S) :- cost_matrix(S,_,_).

% supplier_assignment(S, W): warehouse W supplies store S.
1 { supplier_assignment(S,W) : warehouse(W) } 1 :- store(S).

% A warehouse cannot supply more stores than its capacity.
:- capacity(W,C), C < #count { S : supplier_assignment(S,W) }.

% A warehouse is open exactly when it supplies at least one store; open_warehouses/2
% reports that as 1 or 0.
open_warehouses(W,1) :- supplier_assignment(_,W).
open_warehouses(W,0) :- warehouse(W), not supplier_assignment(_,W).

% Total cost = supply cost of every store + maintenance of the open warehouses.
supply(C) :- C = #sum { Cost,S : supplier_assignment(S,W), cost_matrix(S,W,Cost) }.
opened(K) :- K = #count { W : open_warehouses(W,1) }.
total_cost(C + B * K) :- supply(C), opened(K), building_cost(B).
#minimize { T : total_cost(T) }.

#show total_cost/1.
#show open_warehouses/2.
#show supplier_assignment/2.
