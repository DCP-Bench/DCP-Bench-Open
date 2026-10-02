:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Hidato: a grid is partly filled with numbers. Fill the empty cells with the
% numbers 1..(rows * columns), each used once, so that consecutive numbers sit
% in cells that touch horizontally, vertically or diagonally.
model(Instance, Vars, [x-Rows]) :-
    Puzzle = Instance.puzzle,               % 0 marks an empty cell
    length(Puzzle, R),
    Puzzle = [FirstRow|_],
    length(FirstRow, C),
    Total is R * C,

    % Rows[i][j] is the number written in the cell of row i, column j.
    length(Rows, R),
    maplist({C, Total}/[Row]>>(length(Row, C), Row ins 1..Total), Rows),
    append(Rows, Cells),
    % every number is used once
    all_distinct(Cells),
    % the numbers already given stay where they are
    append(Puzzle, Givens),
    maplist([Given, Cell]>>(Given =:= 0 -> true ; Cell #= Given), Givens, Cells),

    % Spots[k] is the row and the column of the cell that holds number k: the
    % same assignment seen from the numbers' side. Knowing where number k sits
    % tells where number k+1 can sit, which is what makes the search follow the
    % path 1, 2, 3, ... instead of looking for a neighbour of every cell.
    numlist(1, Total, Numbers),
    maplist({R, C, Cells}/[Number, Spot]>>spot(R, C, Cells, Number, Spot), Numbers, Spots),

    % number k+1 is at most one row and one column away from number k. The two
    % cannot be the same cell, because every number has a cell of its own.
    consecutive(Spots, Pairs),
    maplist([(Row1-Col1)-(Row2-Col2)]>>(abs(Row1 - Row2) #=< 1, abs(Col1 - Col2) #=< 1),
            Pairs),

    % the search decides the row and column of number 1, then of number 2, ...
    maplist([Row-Col, [Row, Col]]>>true, Spots, SpotLists),
    append(SpotLists, Vars).

% Search along the path 1, 2, 3, ...
labeling_options([leftmost]).

% spot(+R, +C, +Cells, +Number, -Row-Col): Row-Col is the cell of the R x C grid
% holding Number; Cells lists the grid row by row.
spot(R, C, Cells, Number, Row-Col) :-
    Row in 1..R,
    Col in 1..C,
    Position #= (Row - 1) * C + Col,
    element(Position, Cells, Number).

% consecutive(+List, -Pairs): the pairs X, Y of neighbours in List, written
% X-Y.
consecutive([_], []) :- !.
consecutive([X, Y|Rest], [X-Y|Pairs]) :-
    consecutive([Y|Rest], Pairs).
