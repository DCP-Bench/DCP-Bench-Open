:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Maximum density still life: in Conway's Game of Life, find the pattern with
% the most live cells on an n x m grid that does not change from one
% generation to the next. The rest of the infinite board is dead.
model(Instance, Cells, [grid-Rows], max(Live)) :-
    N = Instance.n,                         % rows of the active grid
    M = Instance.m,                         % columns of the active grid

    % Rows[i][j] is 1 when the cell in row i, column j is alive.
    length(Rows, N),
    cell_rows(Rows, M),
    append(Rows, Cells),

    % every cell of the grid obeys the rules
    numlist(1, N, RowNumbers),
    numlist(1, M, ColumnNumbers),
    rules_for_rows(RowNumbers, ColumnNumbers, N, M, Rows),

    % The dead cells just outside the grid must not be born either: such a
    % cell touches three cells of the grid along the edge (fewer at the ends of
    % the edge), and those must not all be alive. Cells diagonally off a corner
    % touch a single cell of the grid, so they need no rule.
    edge_groups(N, M, Groups),
    not_born_outside(Groups, Rows),

    % the number of live cells, to be maximised
    Total is N * M,
    Live in 0..Total,
    sum(Cells, #=, Live).

% Search the cells row by row, trying a live cell first (a dense pattern is
% found early and improved from there).
labeling_options([leftmost, down]).

% cell_rows(+Rows, +M): every row is a list of M cells that are dead (0) or alive (1).
cell_rows([], _).
cell_rows([Row|Rows], M) :-
    length(Row, M),
    Row ins 0..1,
    cell_rows(Rows, M).

% rules_for_rows(+RowNumbers, +ColumnNumbers, +N, +M, +Rows): the rules hold for
% every cell of the grid.
rules_for_rows([], _, _, _, _).
rules_for_rows([I|Is], ColumnNumbers, N, M, Rows) :-
    rules_for_row(ColumnNumbers, I, N, M, Rows),
    rules_for_rows(Is, ColumnNumbers, N, M, Rows).

rules_for_row([], _, _, _, _).
rules_for_row([J|Js], I, N, M, Rows) :-
    neighbour_cells(N, M, I, J, Coordinates),
    values_at(Coordinates, Rows, Neighbours),
    value_at(I, J, Rows, Cell),
    sum(Neighbours, #=, LiveNeighbours),
    % a live cell needs exactly 2 or 3 live neighbours to stay alive
    Cell #= 1 #==> (LiveNeighbours #>= 2 #/\ LiveNeighbours #=< 3),
    % a dead cell must not have exactly 3 live neighbours (it would be born)
    Cell #= 0 #==> LiveNeighbours #\= 3,
    rules_for_row(Js, I, N, M, Rows).

% not_born_outside(+Groups, +Rows): of the cells in a group, which touch the same
% dead cell outside the grid, not exactly 3 are alive.
not_born_outside([], _).
not_born_outside([Group|Groups], Rows) :-
    values_at(Group, Rows, Touching),
    sum(Touching, #\=, 3),
    not_born_outside(Groups, Rows).

% neighbour_cells(+N, +M, +I, +J, -Coordinates): the cells of an N x M grid next
% to cell (I, J), horizontally, vertically or diagonally, as Row-Column pairs
% (every cell except (I, J) itself).
neighbour_cells(N, M, I, J, Coordinates) :-
    findall(I2-J2,
            (   member(DI, [-1, 0, 1]),
                member(DJ, [-1, 0, 1]),
                \+ ( DI =:= 0, DJ =:= 0 ),
                I2 is I + DI, J2 is J + DJ,
                I2 >= 1, I2 =< N, J2 >= 1, J2 =< M
            ),
            Coordinates).

% edge_groups(+N, +M, -Groups): for each dead cell just outside an edge of the
% N x M grid, the cells of the grid it touches, as Row-Column pairs.
edge_groups(N, M, Groups) :-
    numlist(1, N, Rows),
    numlist(1, M, Columns),
    findall(Group,
            (   % above the first row and below the last row
                member(Row, [1, N]), member(Column, Columns),
                span(M, Column, Span),
                findall(Row-C, member(C, Span), Group)
            ;   % left of the first column and right of the last column
                member(Column, [1, M]), member(Row, Rows),
                span(N, Row, Span),
                findall(R-Column, member(R, Span), Group)
            ),
            Groups).

% span(+Length, +Position, -Positions): the positions 1..Length within one step
% of Position.
span(Length, Position, Positions) :-
    Low is max(1, Position - 1),
    High is min(Length, Position + 1),
    numlist(Low, High, Positions).

% values_at(+Coordinates, +Rows, -Values): the entries of the matrix at the
% given Row-Column pairs.
values_at([], _, []).
values_at([I-J|Coordinates], Rows, [Value|Values]) :-
    value_at(I, J, Rows, Value),
    values_at(Coordinates, Rows, Values).

% value_at(+I, +J, +Rows, ?Value): the entry in row I, column J of the matrix.
value_at(I, J, Rows, Value) :-
    nth1(I, Rows, Row),
    nth1(J, Row, Value).
