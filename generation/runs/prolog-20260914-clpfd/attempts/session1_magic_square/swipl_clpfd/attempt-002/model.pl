:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [square-Rows]) :-
    N = Instance.n,
    Cells is N * N,
    Magic is N * (N * N + 1) // 2,
    length(Rows, N),
    maplist({Cells, N}/[Row]>>(length(Row, N), Row ins 1..Cells), Rows),
    append(Rows, Vars),
    all_distinct(Vars),
    maplist({Magic}/[Row]>>sum(Row, #=, Magic), Rows),
    transpose(Rows, Columns),
    maplist({Magic}/[Column]>>sum(Column, #=, Magic), Columns),
    numlist(1, N, Positions),
    maplist({Rows, N}/[I, Cell]>>cell(Rows, I, I, Cell), Positions, Falling),
    maplist({Rows, N}/[I, Cell]>>(J is N + 1 - I, cell(Rows, I, J, Cell)), Positions, Rising),
    sum(Falling, #=, Magic),
    sum(Rising, #=, Magic).

cell(Rows, I, J, Cell) :-
    nth1(I, Rows, Row),
    nth1(J, Row, Cell).
