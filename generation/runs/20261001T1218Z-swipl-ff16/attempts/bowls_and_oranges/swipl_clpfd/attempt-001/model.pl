:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Bowls and oranges: put m oranges in n bowls standing in a line, at most one
% orange per bowl, so that no three oranges A, B, C have the distance from A to
% B equal to the distance from B to C.
model(Instance, Vars, [x-X]) :-
    N = Instance.n,    % number of bowls
    M = Instance.m,    % number of oranges

    % X[i] = bowl (numbered from 1) holding the i-th orange; the oranges are
    % listed in ascending bowl order
    length(X, M),
    X ins 1..N,
    chain(X, #=<),

    % at most one orange per bowl
    all_distinct(X),

    % no three oranges are evenly spaced: for any i < j < k, the gap from the
    % i-th to the j-th differs from the gap from the j-th to the k-th
    findall(I-J-K, (between(1, M, I), between(1, M, J), I < J,
                    between(1, M, K), J < K), Triples),
    maplist({X}/[I-J-K]>>(nth1(I, X, A), nth1(J, X, B), nth1(K, X, C),
                          B - A #\= C - B),
            Triples),
    Vars = X.
