:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Costas, [costas-Costas]) :-
    N = Instance.n,
    length(Costas, N),
    Costas ins 1..N,
    all_distinct(Costas),
    Rows is N - 2,
    (   Rows >= 1
    ->  numlist(1, Rows, Lags),
        maplist({Costas, N}/[Lag]>>triangle_row(Costas, N, Lag), Lags)
    ;   true
    ).

triangle_row(Costas, N, Lag) :-
    First is Lag + 1,
    numlist(First, N, Positions),
    maplist({Costas, Lag}/[J, D]>>difference(Costas, Lag, J, D), Positions, Row),
    all_distinct(Row).

difference(Costas, Lag, J, D) :-
    nth1(J, Costas, Later),
    Earlier is J - Lag,
    nth1(Earlier, Costas, Sooner),
    D #= Later - Sooner.
