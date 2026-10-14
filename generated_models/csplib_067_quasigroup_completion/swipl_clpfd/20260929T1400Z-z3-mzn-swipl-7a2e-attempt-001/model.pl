:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Quasigroup completion: fill the empty cells of a partially filled N x N grid
% so that every row and every column contains each of 1..N exactly once (a
% Latin square).
model(Instance, Vars, [puzzle-Rows]) :-
    N = Instance.'N',          % size of the square
    Start = Instance.start,    % given cells; 0 marks an empty cell

    % Rows[i][j] = the number in cell (i, j), from 1 to N
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 1..N), Rows),

    % the given cells keep their value
    maplist([Row, StartRow]>>maplist(given, Row, StartRow), Rows, Start),

    % each row holds different numbers
    maplist(all_distinct, Rows),
    % each column holds different numbers
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    append(Rows, Vars).

% an empty cell (0 in the data) is left free; any other value is fixed
given(_, 0) :- !.
given(Cell, Value) :- Cell #= Value.
