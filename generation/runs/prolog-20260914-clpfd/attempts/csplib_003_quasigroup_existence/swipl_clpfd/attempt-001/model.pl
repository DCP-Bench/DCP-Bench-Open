:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [quasigroup-Rows]) :-
    M = Instance.m,
    Top is M - 1,
    length(Rows, M),
    maplist({M, Top}/[Row]>>(length(Row, M), Row ins 0..Top), Rows),
    append(Rows, Vars),
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    findall(A-B, (between(0, Top, A), between(0, Top, B)), Cells),
    maplist(qg3(Vars, M), Cells).

% (a * b) * (b * a) = a, as an element/3 lookup on the flattened table: the
% values are 0-based and element/3 is 1-based, so the cell holding row Ab and
% column Ba is at Ab * M + Ba + 1.
qg3(Flat, M, A-B) :-
    entry(Flat, M, A, B, Ab),
    entry(Flat, M, B, A, Ba),
    Position #= Ab * M + Ba + 1,
    element(Position, Flat, A).

entry(Flat, M, Row, Column, Value) :-
    Position is Row * M + Column + 1,
    nth1(Position, Flat, Value).
