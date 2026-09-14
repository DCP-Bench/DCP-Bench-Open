:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [a-As, b-Bs]) :-
    L = Instance.l,
    Shifts is (L - 1) // 2,
    length(As, L),
    length(Bs, L),
    append(As, Bs, Vars),
    Vars ins -1..1,
    maplist([V]>>(V #\= 0), Vars),
    sum(As, #=, 1),
    sum(Bs, #=, 1),
    numlist(1, Shifts, Lags),
    maplist({As, Bs, L}/[S]>>correlated(As, Bs, L, S), Lags).

correlated(As, Bs, L, S) :-
    periodic(As, L, S, First),
    periodic(Bs, L, S, Second),
    First + Second #= -2.

% PAF(X, s) = sum_i x_i * x_{(i + s) mod l}.
periodic(Xs, L, S, Total) :-
    numlist(1, L, Positions),
    maplist({Xs, L, S}/[I, Product]>>shifted_product(Xs, L, S, I, Product), Positions, Products),
    sum(Products, #=, Total).

shifted_product(Xs, L, S, I, Product) :-
    nth1(I, Xs, Here),
    J is ((I - 1 + S) mod L) + 1,
    nth1(J, Xs, There),
    Product #= Here * There.
