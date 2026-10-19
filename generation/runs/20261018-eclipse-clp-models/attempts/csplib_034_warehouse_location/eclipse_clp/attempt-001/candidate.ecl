% Warehouse Location (CSPLib 034) in ECLiPSe with lib(ic) and lib(listut).
% Decide which warehouses to open; every store is supplied by exactly one open
% warehouse within that warehouse's capacity. Minimise the total cost: the
% maintenance cost of the opened warehouses plus the supply cost of every store.
% Instance fields: n_suppliers (warehouses), n_stores, building_cost (maintenance
% cost per opened warehouse), capacity (stores each warehouse can supply),
% cost_matrix[store][warehouse] (supply cost).

:- lib(ic).
:- lib(listut).

model(Instance, Vars, Outputs, min(Total)) :-
    memberchk(n_suppliers-NS, Instance),
    memberchk(n_stores-NT, Instance),
    memberchk(building_cost-BC, Instance),
    memberchk(capacity-Cap, Instance),
    memberchk(cost_matrix-CM, Instance),
    MaxW is NS - 1,
    % open_warehouses: one 0/1 variable per warehouse
    length(Open, NS),
    Open :: 0..1,
    % supplier_assignment: the warehouse (0-based) serving each store
    length(Assign, NT),
    Assign :: 0..MaxW,
    % supply cost of each store, from the cost of its assigned warehouse
    length(Costs, NT),
    (
        foreach(Row, CM), foreach(Cost, Costs), foreach(A, Assign)
    do
        Idx #= A + 1,
        element(Idx, Row, Cost)
    ),
    % a store can only be supplied by a warehouse that is open
    (
        foreach(A, Assign), param(Open)
    do
        Idx #= A + 1,
        element(Idx, Open, 1)
    ),
    % every warehouse serves at most its capacity of stores
    capacity_limits(Cap, 0, Assign),
    % total cost: maintenance of the open warehouses plus all supply costs
    Total #= BC * sum(Open) + sum(Costs),
    append(Open, Assign, Vars),
    Outputs = [open_warehouses-Open, supplier_assignment-Assign, total_cost-Total].

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% at most CapW stores are supplied by warehouse W, for each warehouse in turn
capacity_limits([], _, _).
capacity_limits([CapW | Caps], W, Assign) :-
    store_indicators(Assign, W, Bs),
    sum(Bs) #=< CapW,
    W1 is W + 1,
    capacity_limits(Caps, W1, Assign).

% Bs[s] = 1 exactly when store s is supplied by warehouse W
store_indicators([], _, []).
store_indicators([A | As], W, [B | Bs]) :-
    B #= (A #= W),
    store_indicators(As, W, Bs).
