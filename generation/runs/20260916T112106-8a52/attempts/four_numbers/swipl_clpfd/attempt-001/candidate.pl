:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Four numbers: find three values whose subsets sum to every given number.
model(Instance, Vars, [x-Xs]) :-
    Numbers = Instance.numbers,
    length(Xs, 3),
    Xs ins 1..10,
    % One subset indicator row per target number.
    maplist({Xs}/[Target, Row]>>subset_sum(Xs, Target, Row), Numbers, Rows),
    append(Rows, RowVars),
    append(Xs, RowVars, Vars).

subset_sum(Xs, Target, Row) :-
    length(Row, 3),
    Row ins 0..1,
    maplist([X, Chosen, Part]>>(Part #= X * Chosen), Xs, Row, Parts),
    sum(Parts, #=, Target).
