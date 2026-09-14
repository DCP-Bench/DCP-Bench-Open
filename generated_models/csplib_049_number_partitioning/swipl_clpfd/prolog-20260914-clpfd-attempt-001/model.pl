:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, ['A'-Xs, 'B'-Ys]) :-
    N = Instance.n,
    Half is N // 2,
    length(Xs, Half),
    length(Ys, Half),
    append(Xs, Ys, Vars),
    Vars ins 1..N,
    all_distinct(Vars),
    sum(Xs, #=, Total),
    sum(Ys, #=, Total),
    maplist([V, S]>>(S #= V * V), Xs, SquaresX),
    maplist([V, S]>>(S #= V * V), Ys, SquaresY),
    sum(SquaresX, #=, Squares),
    sum(SquaresY, #=, Squares),
    % Implied by the partition: each half carries half of each total.
    4 * Total #= N * (N + 1),
    12 * Squares #= N * (N + 1) * (2 * N + 1).
