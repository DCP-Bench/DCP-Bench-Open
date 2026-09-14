:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Queens, [queens-Queens]) :-
    N = Instance.n,
    length(Queens, N),
    Queens ins 1..N,
    numlist(1, N, Rows),
    % The two diagonals, as auxiliary variables: all_distinct/1 takes variables
    % and integers, not expressions.
    maplist([Q, I, D]>>(D #= Q - I), Queens, Rows, Downs),
    maplist([Q, I, U]>>(U #= Q + I), Queens, Rows, Ups),
    all_distinct(Queens),
    all_distinct(Downs),
    all_distinct(Ups).
