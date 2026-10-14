:- use_module(library(clpfd)).
:- use_module(library(lists)).
:- use_module(library(pairs)).

% Autoref: find a series s[0..n+1] in which every i from 0 to n occurs exactly
% s[i] times, and whose last element s[n+1] equals m.
model(Instance, S, [s-S]) :-
    N = Instance.n,
    M = Instance.m,                  % required value of the last element
    Length is N + 2,

    % the series has n + 2 positions; every value lies between 0 and n
    length(S, Length),
    S ins 0..N,

    % the last element is m
    last(S, M),

    % the value i occurs exactly s[i] times in the series: the first n + 1
    % entries of the series are the counts for the values 0..n
    Counted is N + 1,
    length(Counts, Counted),
    append(Counts, _, S),
    numlist(0, N, Values),
    pairs_keys_values(Wanted, Values, Counts),
    global_cardinality(S, Wanted).
