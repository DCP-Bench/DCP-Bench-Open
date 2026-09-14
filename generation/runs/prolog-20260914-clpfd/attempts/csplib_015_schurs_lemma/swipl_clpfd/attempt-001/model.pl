:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

model(Instance, Balls, [balls-Balls]) :-
    N = Instance.n,
    C = Instance.c,
    length(Balls, N),
    Balls ins 1..C,
    % The triples are collected first: constraints posted inside forall/2 would
    % be undone by its own backtracking.
    findall(X-Y, (between(1, N, X), between(1, N, Y), X + Y =< N), Triples),
    maplist(apart(Balls), Triples).

apart(Balls, X-Y) :-
    Z is X + Y,
    nth1(X, Balls, First),
    nth1(Y, Balls, Second),
    nth1(Z, Balls, Sum),
    (First #\= Second) #\/ (First #\= Sum) #\/ (Second #\= Sum).
