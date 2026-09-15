:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Network assignment: spend each person's hours in full, meet each project's
% demand exactly, respect the per-pair capacity, and pay as little as possible.
model(Instance, Vars, [assign-Rows, total_cost-TotalCost], min(TotalCost)) :-
    Supply = Instance.supply,
    Demand = Instance.demand,
    Cost = Instance.cost,
    Limit = Instance.limit,
    length(Supply, People),
    length(Demand, Projects),
    length(Rows, People),
    % Hours per pair keep the reference's declared 0..10 domain.
    maplist({Projects}/[Row]>>(length(Row, Projects), Row ins 0..10), Rows),
    append(Rows, Vars),
    maplist(within_limit, Rows, Limit),
    maplist([Row, Hours]>>sum(Row, #=, Hours), Rows, Supply),
    transpose(Rows, Columns),
    maplist([Column, Hours]>>sum(Column, #=, Hours), Columns, Demand),
    maplist(row_cost, Rows, Cost, RowCosts),
    sum(RowCosts, #=, TotalCost).

within_limit(Row, Caps) :-
    maplist([H, Cap]>>(H #=< Cap), Row, Caps).

row_cost(Row, Prices, Spent) :-
    scalar_product(Prices, Row, #=, Spent).
