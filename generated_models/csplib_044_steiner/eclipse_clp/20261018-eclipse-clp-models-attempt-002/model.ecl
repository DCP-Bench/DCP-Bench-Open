% Ternary Steiner problem (csplib_044_steiner), ECLiPSe with lib(ic).
% Find a set of n(n-1)/6 triples of distinct elements from 1..n such that any two
% triples have at most one common element. The output sets[i][j] is 1 when element j
% is part of triple i. n is read from the instance.

:- lib(ic).
:- lib(listut).
:- lib(lists).

model(Instance, Vars, [sets-Rows]) :-
    memberchk(n-N, Instance),
    T is N*(N-1)//6,
    length(Rows, T),
    % Each triple is a row of a 0/1 matrix over the n elements, with exactly three elements.
    ( foreach(R, Rows), param(N) do
        length(R, N),
        R :: 0..1,
        sum(R) #= 3
    ),
    % any two triples have at most one common element
    share_at_most_one(Rows),
    % every pair of elements lies in exactly one triple (implied by the counts, stated for propagation)
    cover_pairs(Rows, N),
    % every element lies in (n-1)/2 triples (implied by the pair condition, stated for propagation)
    degrees(Rows, N),
    % labelling order: element by element
    columns(Rows, N, Vars).

columns(Rows, N, Vars) :-
    ( for(K, 1, N), foreach(Col, ColLists), param(Rows) do
        ( foreach(R, Rows), foreach(X, Col), param(K) do
            nth1(K, R, X)
        )
    ),
    flatten(ColLists, Vars).

degrees(Rows, N) :-
    ( for(K, 1, N), param(Rows, N) do
        ( foreach(R, Rows), foreach(X, Col), param(K) do
            nth1(K, R, X)
        ),
        sum(Col) #= (N-1)//2
    ).

share_at_most_one([]).
share_at_most_one([R|Rs]) :-
    ( foreach(R2, Rs), param(R) do
        shared_at_most_one(R, R2)
    ),
    share_at_most_one(Rs).

shared_at_most_one(R1, R2) :-
    ( foreach(X, R1), foreach(Y, R2), foreach(P, Ps) do
        P #= X*Y
    ),
    sum(Ps) #=< 1.

cover_pairs(Rows, N) :-
    ( for(K, 1, N), param(Rows, N) do
        K1 is K+1,
        ( for(L, K1, N), param(Rows, K) do
            pair_once(Rows, K, L)
        )
    ).

pair_once(Rows, K, L) :-
    ( foreach(R, Rows), foreach(P, Ps), param(K, L) do
        nth1(K, R, XK),
        nth1(L, R, XL),
        P #= XK*XL
    ),
    sum(Ps) #= 1.

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_max, complete, []).
