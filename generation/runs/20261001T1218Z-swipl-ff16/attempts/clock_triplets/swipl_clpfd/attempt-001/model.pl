:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Clock triplets: arrange the numbers 1 to 12 around the face of a clock so that
% no three neighbouring numbers add up to more than 21.
model(_Instance, Clock, [x-Clock]) :-
    % The 12 hours and the limit 21 belong to the problem (there are no
    % instance fields): 21 is the smallest value the largest sum of three
    % neighbours can take.
    N = 12,
    MaxSum = 21,

    % Clock[i] is the number at position i; the positions go around the face.
    length(Clock, N),
    Clock ins 1..N,
    % every number is on the clock once
    all_distinct(Clock),

    % no three neighbouring numbers, wrapping around the face from the last
    % position to the first, add up to more than the limit
    Clock = [First, Second|_],
    append(Clock, [First, Second], Wrapped),
    triplets_within(Wrapped, MaxSum).

% triplets_within(+Numbers, +Max): every three consecutive entries add up to at
% most Max.
triplets_within([A, B, C|Rest], Max) :-
    !,
    A + B + C #=< Max,
    triplets_within([B, C|Rest], Max).
triplets_within(_, _).
