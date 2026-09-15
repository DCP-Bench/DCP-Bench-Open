:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Assignment costs: every task goes to exactly one person and no person takes
% two tasks, at minimum total cost.
model(Instance, Vars, [x-Rows], min(TotalCost)) :-
    Cost = Instance.cost,
    length(Cost, NumTasks),
    Cost = [FirstRow|_],
    length(FirstRow, NumPeople),
    length(Rows, NumTasks),
    maplist({NumPeople}/[Row]>>(length(Row, NumPeople), Row ins 0..1), Rows),
    append(Rows, Vars),
    % Exactly one assignment per task; at most one per person.
    maplist([Row]>>sum(Row, #=, 1), Rows),
    transpose(Rows, Columns),
    maplist([Column]>>sum(Column, #=<, 1), Columns),
    maplist(row_cost, Rows, Cost, RowCosts),
    sum(RowCosts, #=, TotalCost),
    TotalCost #>= 0.

row_cost(Row, Prices, Spent) :-
    scalar_product(Prices, Row, #=, Spent).
