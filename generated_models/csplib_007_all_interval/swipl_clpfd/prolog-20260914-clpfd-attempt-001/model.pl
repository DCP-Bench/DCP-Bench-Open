:- use_module(library(clpfd)).
:- use_module(library(lists)).

model(Instance, Xs, [x-Xs, diffs-Ds]) :-
    N = Instance.n,
    Top is N - 1,
    length(Xs, N),
    Xs ins 0..Top,
    length(Ds, Top),
    Ds ins 1..Top,
    all_distinct(Xs),
    all_distinct(Ds),
    intervals(Xs, Ds).

intervals([_], []).
intervals([A, B|Rest], [D|Ds]) :-
    D #= abs(B - A),
    intervals([B|Rest], Ds).
