:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Maximum density still life: in Conway's Game of Life, find the pattern with
% the most live cells on an n x m grid that does not change from one
% generation to the next. The rest of the infinite board is dead.
model(Instance, Cells, [grid-Rows], max(Live)) :-
    N = Instance.n,                         % rows of the active grid
    M = Instance.m,                         % columns of the active grid

    % Rows[i][j] is 1 when the cell in row i, column j is alive.
    length(Rows, N),
    maplist({M}/[Row]>>(length(Row, M), Row ins 0..1), Rows),
    append(Rows, Cells),

    % The grid with a ring of dead cells around it. The dead cells next to the
    % grid must not be born either, so the rules are posted on the grid and
    % the ring together; cells further out see no live cell.
    Width is M + 2,
    length(DeadRow, Width),
    maplist(=(0), DeadRow),
    maplist([Row, Padded]>>append([[0], Row, [0]], Padded), Rows, PaddedRows),
    append([[DeadRow], PaddedRows, [DeadRow]], Board),

    % The rules: a live cell needs exactly 2 or 3 live neighbours to stay
    % alive; a dead cell must not have exactly 3 live neighbours (it would be
    % born).
    % every cell of the board obeys the rules
    BoardRows is N + 2,
    BoardColumns is M + 2,
    numlist(1, BoardRows, RowNumbers),
    numlist(1, BoardColumns, ColumnNumbers),
    findall(I-J, (member(I, RowNumbers), member(J, ColumnNumbers)), Positions),
    maplist({Board, BoardRows, BoardColumns}/[I-J]>>
                obeys_rules(Board, BoardRows, BoardColumns, I, J),
            Positions),

    % the number of live cells, to be maximised
    Total is N * M,
    Live in 0..Total,
    sum(Cells, #=, Live).

% Search the cells row by row, trying a live cell first (a dense pattern is
% found early and improved from there).
labeling_options([leftmost, down]).

% obeys_rules(+Board, +R, +C, +I, +J): the cell in row I, column J of the R x C
% board and the number of live cells next to it obey the rules.
obeys_rules(Board, R, C, I, J) :-
    findall(I2-J2,
            (   member(DI, [-1, 0, 1]),
                member(DJ, [-1, 0, 1]),
                ( DI =\= 0 ; DJ =\= 0 ),
                I2 is I + DI, J2 is J + DJ,
                I2 >= 1, I2 =< R, J2 >= 1, J2 =< C
            ),
            Coordinates),
    maplist({Board}/[A-B, Neighbour]>>board_cell(Board, A, B, Neighbour),
            Coordinates, Neighbours),
    board_cell(Board, I, J, Cell),
    sum(Neighbours, #=, LiveNeighbours),
    % a live cell keeps 2 or 3 live neighbours; a dead cell is not born from 3
    Cell #= 1 #==> (LiveNeighbours #>= 2 #/\ LiveNeighbours #=< 3),
    Cell #= 0 #==> LiveNeighbours #\= 3.

% board_cell(+Board, +I, +J, ?Cell): Cell is the entry in row I, column J.
board_cell(Board, I, J, Cell) :-
    nth1(I, Board, Row),
    nth1(J, Row, Cell).
