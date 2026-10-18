% Bowls and oranges: bowls are placed in a line at 1 meter intervals, numbered
% 1..n. Place m oranges in the bowls, at most one orange per bowl, so that no
% three oranges A, B, C have distance(A,B) = distance(B,C). Output the bowls
% holding the oranges in ascending order.

:- lib(ic).

model(Instance, Xs, [x-Xs]) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    length(Xs, M),

    % place all oranges in bowls 1..n, in ascending order, at most one per bowl
    Xs :: 1..N,
    bo_ascending(Xs),

    % no three oranges A, B, C such that the distance between A and B is equal
    % to the distance between B and C: for a < b < c in the order of the bowls,
    % b is not the midpoint of a and c
    bo_no_progression(Xs, []).

bo_ascending([]).
bo_ascending([_]).
bo_ascending([A, B | T]) :-
    A #< B,
    bo_ascending([B | T]).

bo_no_progression([], _).
bo_no_progression([B | Suffix], Prefix) :-
    ( foreach(A, Prefix), param(B, Suffix) do
        ( foreach(C, Suffix), param(A, B) do
            2 * B #\= A + C
        )
    ),
    bo_no_progression(Suffix, [B | Prefix]).
