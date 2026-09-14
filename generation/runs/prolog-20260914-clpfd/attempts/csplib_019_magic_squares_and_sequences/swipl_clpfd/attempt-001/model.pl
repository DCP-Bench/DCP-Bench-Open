:- use_module(library(clpfd)).
:- use_module(library(pairs)).
:- use_module(library(lists)).

model(Instance, Xs, [x-Xs]) :-
    N = Instance.n,
    Top is N - 1,
    length(Xs, N),
    Xs ins 0..Top,
    numlist(0, Top, Values),
    % Value i occurs x[i] times: the counts of the cardinality constraint are
    % the sequence itself.
    pairs_keys_values(Counts, Values, Xs),
    global_cardinality(Xs, Counts).
