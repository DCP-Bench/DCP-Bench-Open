:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Warehouse location: decide which candidate warehouses to open and which open
% warehouse supplies each store, so that no warehouse serves more stores than
% its capacity and the maintenance cost of the open warehouses plus the supply
% costs of all stores is minimal.
model(Instance, Vars,
      [total_cost-Total, open_warehouses-Open, supplier_assignment-Assignment], min(Total)) :-
    NSuppliers = Instance.n_suppliers,   % candidate warehouses
    NStores = Instance.n_stores,
    BuildingCost = Instance.building_cost,   % maintenance cost of one open warehouse
    Capacity = Instance.capacity,            % most stores each warehouse can supply
    CostMatrix = Instance.cost_matrix,       % CostMatrix[store][warehouse] = supply cost

    % Assignment[s] = the warehouse (numbered from 0) that supplies store s
    Top is NSuppliers - 1,
    length(Assignment, NStores),
    Assignment ins 0..Top,
    % Open[w] is 1 when warehouse w is open
    length(Open, NSuppliers),
    Open ins 0..1,

    % a warehouse cannot supply more stores than its capacity, and it is open
    % exactly when it supplies at least one store; this also forbids supplying
    % a store from a closed warehouse
    numlist(0, Top, Warehouses),
    maplist({Assignment, NStores}/[W, IsOpen, Cap, Supplied]>>(
                Supplied in 0..NStores,
                maplist({W}/[A, Hit]>>(Hit #<==> (A #= W)), Assignment, Hits),
                sum(Hits, #=, Supplied),
                Supplied #=< Cap,
                IsOpen #<==> (Supplied #> 0)),
            Warehouses, Open, Capacity, Counts),

    % supply cost of each store: the entry of its row picked by the warehouse it uses
    % (element/3 counts from 1)
    maplist([A, Row, Cost]>>(Index #= A + 1, element(Index, Row, Cost)), Assignment, CostMatrix, StoreCosts),

    % total cost = supply costs + maintenance of the open warehouses
    append(CostMatrix, AllCosts),
    sum_list(AllCosts, CostSum),
    Bound is CostSum + NSuppliers * BuildingCost,
    Total in 0..Bound,
    sum(StoreCosts, #=, SupplyCost),
    sum(Open, #=, HowManyOpen),
    Total #= SupplyCost + BuildingCost * HowManyOpen,
    append([Assignment, Open, Counts, StoreCosts, [Total]], Vars).
