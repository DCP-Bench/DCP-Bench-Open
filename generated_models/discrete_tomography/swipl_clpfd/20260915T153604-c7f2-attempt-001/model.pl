:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Discrete tomography: reconstruct a 0/1 picture from its row and column sums.
model(Instance, Vars, [matrix-Rows]) :-
    RowSums = Instance.row_sums,
    ColSums = Instance.col_sums,
    length(RowSums, R),
    length(ColSums, C),
    length(Rows, R),
    maplist({C}/[Row]>>(length(Row, C), Row ins 0..1), Rows),
    append(Rows, Vars),
    maplist([Row, Wanted]>>sum(Row, #=, Wanted), Rows, RowSums),
    transpose(Rows, Columns),
    maplist([Column, Wanted]>>sum(Column, #=, Wanted), Columns, ColSums).
