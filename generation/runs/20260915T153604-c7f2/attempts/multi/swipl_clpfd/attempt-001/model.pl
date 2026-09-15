:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Multicommodity transport: ship several products from origins to
% destinations, within per-product supply, per-pair capacity and demand, at
% minimum shipping cost.
model(Instance, Vars, [total_cost-TotalCost], min(TotalCost)) :-
    Supply = Instance.supply,
    Demand = Instance.demand,
    Limit = Instance.limit,
    Cost = Instance.cost,
    length(Supply, Origins),
    length(Demand, Destinations),
    Supply = [FirstSupply|_],
    length(FirstSupply, Products),
    append(Supply, SupplyFlat),
    max_list(SupplyFlat, MaxSupply),
    % Routes[i][j] is the list of per-product amounts from origin i to j.
    length(Routes, Origins),
    maplist({Destinations, Products, MaxSupply}/[Row]>>
                (length(Row, Destinations),
                 maplist({Products, MaxSupply}/[Cell]>>
                             (length(Cell, Products), Cell ins 0..MaxSupply),
                         Row)),
            Routes),
    append(Routes, RouteRows),
    append(RouteRows, Vars),
    % Supply: what leaves an origin, per product.
    maplist(origin_limit, Routes, Supply),
    % Demand: what arrives at a destination, per product.
    transpose(Routes, ByDestination),
    maplist(destination_need, ByDestination, Demand),
    % Capacity: the whole load on one origin-destination pair.
    maplist(pair_limit, Routes, Limit),
    maplist(route_cost, Routes, Cost, RowCosts),
    sum(RowCosts, #=, TotalCost).

origin_limit(Row, Available) :-
    transpose(Row, ByProduct),
    maplist([Amounts, Cap]>>sum(Amounts, #=<, Cap), ByProduct, Available).

destination_need(Column, Needed) :-
    transpose(Column, ByProduct),
    maplist([Amounts, Need]>>sum(Amounts, #>=, Need), ByProduct, Needed).

pair_limit(Row, Caps) :-
    maplist([Cell, Cap]>>sum(Cell, #=<, Cap), Row, Caps).

route_cost(Row, Prices, Spent) :-
    maplist([Cell, Price, Part]>>scalar_product(Price, Cell, #=, Part),
            Row, Prices, Parts),
    sum(Parts, #=, Spent).
