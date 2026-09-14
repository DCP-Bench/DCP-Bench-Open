:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Sequence, [sequence-Sequence], min(Energy)) :-
    N = Instance.n,
    length(Sequence, N),
    Sequence ins -1..1,
    maplist([V]>>(V #\= 0), Sequence),
    Last is N - 1,
    numlist(1, Last, Lags),
    maplist({Sequence, N}/[S, Square]>>energy(Sequence, N, S, Square), Lags, Squares),
    sum(Squares, #=, Energy).

energy(Sequence, N, S, Square) :-
    periodic(Sequence, N, S, Correlation),
    Square #= Correlation * Correlation.

% PAF(x, s) = sum_i x_i * x_{(i + s) mod n}.
periodic(Xs, N, S, Total) :-
    numlist(1, N, Positions),
    maplist({Xs, N, S}/[I, Product]>>shifted_product(Xs, N, S, I, Product), Positions, Products),
    sum(Products, #=, Total).

shifted_product(Xs, N, S, I, Product) :-
    nth1(I, Xs, Here),
    J is ((I - 1 + S) mod N) + 1,
    nth1(J, Xs, There),
    Product #= Here * There.
