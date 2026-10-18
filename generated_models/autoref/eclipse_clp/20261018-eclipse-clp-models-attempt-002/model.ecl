% autoref: self-referential series. Given n > 0 and m >= 0, find a series
% S = (s0, s1, ..., sn, sn+1) of n+2 terms such that there are si occurrences
% of i in S for each i from 0 to n, and sn+1 = m. Output the series s.
% The terms are values 0..n of the series alphabet (the description's own
% indices), so every term ranges over 0..n.

:- lib(ic).
:- lib(listut).

model(Instance, S, [s-S]) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    N2 is N + 2,
    length(S, N2),
    S :: 0..N,

    % the last term sn+1 equals m
    N1 is N + 1,
    nth0(N1, S, SLast),
    SLast #= M,

    % there are si occurrences of i in S for each i from 0 to n
    ( for(I, 0, N), param(S) do
        nth0(I, S, Si),
        ( foreach(Xj, S), foreach(Bj, Bs), param(I) do
            Bj #= (Xj #= I)
        ),
        sum(Bs) #= Si
    ).

search_goal(S) :-
    search(S, 0, first_fail, indomain_min, complete, []).
