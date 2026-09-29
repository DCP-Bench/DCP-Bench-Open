:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Maximum density still life: on an n x m active area of Conway's Game of Life,
% find the pattern with the most live cells that is stable (unchanged in the
% next generation). Cells outside the area are dead but still obey the rules.
model(Instance, Vars, [grid-Rows], max(Live)) :-
    N = Instance.n,   % rows of the active area
    M = Instance.m,   % columns of the active area

    % Rows[i][j] is 1 when the cell is alive
    length(Rows, N),
    maplist({M}/[Row]>>(length(Row, M), Row ins 0..1), Rows),
    append(Rows, Vars0),

    % cells inside the area stay as they are
    numlist(1, N, RowNumbers),
    numlist(1, M, ColumnNumbers),
    findall(I-J, (member(I, RowNumbers), member(J, ColumnNumbers)), Cells),
    maplist({Rows, N, M}/[I-J]>>(
                nth1(I, Rows, Row), nth1(J, Row, Cell),
                findall(A-B, (between(-1, 1, DA), between(-1, 1, DB), \+ (DA =:= 0, DB =:= 0),
                              A is I + DA, B is J + DB, A >= 1, A =< N, B >= 1, B =< M), Around),
                maplist({Rows}/[A-B, Value]>>(nth1(A, Rows, RowA), nth1(B, RowA, Value)), Around, Neighbours),
                sum(Neighbours, #=, Count),
                % a live cell survives only with 2 or 3 live neighbours
                Cell #==> (Count #>= 2 #/\ Count #=< 3),
                % a dead cell must not have exactly 3 live neighbours, or it would be born
                (Cell #= 0) #==> (Count #\= 3)), Cells),

    % dead cells just outside the area must not be born either. The cells that
    % touch the area along its top and bottom edges see three cells of the
    % first / last row, those along the left and right edges three cells of the
    % first / last column; the four outer corners see one cell and never reach 3.
    Rows = [FirstRow|_],
    last(Rows, LastRow),
    transpose(Rows, Columns),
    Columns = [FirstColumn|_],
    last(Columns, LastColumn),
    maplist(edge_not_three, [FirstRow, LastRow, FirstColumn, LastColumn]),

    % the number of live cells, to be maximised
    Cells0 is N * M,
    Live in 0..Cells0,
    sum(Vars0, #=, Live),
    append(Vars0, [Live], Vars).

% no three consecutive cells (or the one or two at an end) of an edge add up to 3
edge_not_three(Edge) :-
    length(Edge, Length),
    numlist(1, Length, Positions),
    maplist({Edge, Length}/[P]>>(Low is max(1, P - 1), High is min(Length, P + 1),
                                 findall(Q, between(Low, High, Q), Window),
                                 maplist({Edge}/[Q, V]>>nth1(Q, Edge, V), Window, Values),
                                 sum(Values, #\=, 3)), Positions).
