:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Killer sudoku: fill a sudoku grid with 1..9 so that each row, column and 3x3
% box holds every digit once, and each cage of cells adds up to its target with
% no digit repeated inside the cage.
model(Instance, Vars, [x-Rows]) :-
    N = Instance.n,               % side of the grid
    Cages = Instance.problem,     % [Target, [[Row, Column], ...]] with cells counted from 1
    Box is truncate(sqrt(N)),     % side of a box

    % Rows[r][c] = the digit in cell (r, c)
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 1..N), Rows),

    % each row and each column holds different digits
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),

    % each box holds different digits: split the rows into bands of Box rows, then each band into boxes
    bands(Rows, Box, Bands),
    maplist({Box}/[Band]>>(transpose(Band, BandColumns), boxes(BandColumns, Box)), Bands),

    % each cage adds up to its target and holds different digits
    maplist({Rows}/[[Target, Cells]]>>(
                maplist({Rows}/[[R, C], Cell]>>(nth1(R, Rows, Row), nth1(C, Row, Cell)), Cells, Cage),
                sum(Cage, #=, Target),
                all_distinct(Cage)), Cages),
    append(Rows, Vars).

% bands(+Rows, +Size, -Bands): consecutive groups of Size rows
bands([], _, []).
bands(Rows, Size, [Band|Bands]) :-
    length(Band, Size),
    append(Band, Rest, Rows),
    bands(Rest, Size, Bands).

% boxes(+Columns, +Size): every group of Size columns of a band holds different digits
boxes([], _).
boxes(Columns, Size) :-
    length(Group, Size),
    append(Group, Rest, Columns),
    append(Group, Cells),
    all_distinct(Cells),
    boxes(Rest, Size).
