:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Among: exactly m of the n entries of x must take a value drawn from v; the
% rest are free within the domain.
model(Instance, Xs, [x-Xs]) :-
    N = Instance.n,
    M = Instance.m,
    Wanted = Instance.v,
    length(Xs, N),
    % Domain 0..7 comes from the problem statement, which fixes it for every
    % instance; the reference declares the same range.
    Xs ins 0..7,
    % One count per position, summed as the reference sums over (position,
    % wanted value) pairs.  maplist rather than findall, so the reified
    % constraints reach the decision variables rather than copies of them.
    maplist({Wanted}/[X, Count]>>hits(X, Wanted, Count), Xs, Counts),
    sum(Counts, #=, M).

hits(X, Wanted, Count) :-
    maplist({X}/[V, B]>>(X #= V #<==> B), Wanted, Bs),
    sum(Bs, #=, Count).
