% All-interval series (CSPLib 007). Given n, find a series s = (s_1, ..., s_n)
% of pitch-classes 0..n-1 that is a permutation of Z_n, such that the interval
% vector v = (|s_2 - s_1|, ..., |s_n - s_{n-1}|) is a permutation of 1..n-1.
% Outputs: x = the series s, diffs = the interval vector v.
:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.

model(Instance, Vars, [x-X, diffs-D]) :-
    memberchk(n-N, Instance),
    N1 is N - 1,
    length(X, N),
    X :: 0..N1,
    length(D, N1),
    D :: 1..N1,
    % s is a permutation of Z_n = {0, 1, ..., n-1}
    alldifferent(X),
    % the interval vector v: each interval is the absolute difference of neighbours
    append(Prev, [_], X),
    X = [_|Next],
    ( foreach(P, Prev), foreach(Q, Next), foreach(Dd, D) do
        Dd #= abs(Q - P)
    ),
    % v is a permutation of 1..n-1
    alldifferent(D),
    append(X, D, Vars).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
