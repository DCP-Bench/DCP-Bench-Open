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

    % The rules as pairs [live neighbours, state of the cell]: a dead cell
    % must not have exactly 3 live neighbours (it would be born); a live cell
    % needs exactly 2 or 3 live neighbours to stay alive.
    findall([Count, 0], (between(0, 8, Count), Count =\= 3), DeadRules),
    append(DeadRules, [[2, 1], [3, 1]], StillLifeTable),

    % every cell of the grid obeys the rules
    numlist(1, N, RowNumbers),
    numlist(1, M, ColumnNumbers),
    findall(I-J, (member(I, RowNumbers), member(J, ColumnNumbers)), Positions),
    maplist({Rows, N, M, StillLifeTable}/[I-J]>>
                (neighbour_cells(N, M, I, J, Coordinates),
                 cells_at(Rows, Coordinates, Neighbours),
                 cells_at(Rows, [I-J], [Cell]),
                 sum(Neighbours, #=, LiveNeighbours),
                 tuples_in([[LiveNeighbours, Cell]], StillLifeTable)),
            Positions),

    % The dead cells just outside the grid must not be born either: such a
    % cell touches three cells of the grid along the edge (fewer at the ends of
    % the edge), and those must not all be alive. Cells diagonally off a corner
    % touch a single cell of the grid, so they need no rule.
    edge_groups(N, M, Edges),
    maplist({Rows}/[Edge]>>(cells_at(Rows, Edge, Touching), sum(Touching, #\=, 3)), Edges),

    % the number of live cells, to be maximised
    Total is N * M,
    Live in 0..Total,
    sum(Cells, #=, Live).

% Search the cells row by row, trying a live cell first (a dense pattern is
% found early and improved from there).
labeling_options([leftmost, down]).

% neighbour_cells(+N, +M, +I, +J, -Coordinates): the cells of an N x M grid next
% to cell (I, J), horizontally, vertically or diagonally, as Row-Column pairs.
neighbour_cells(N, M, I, J, Coordinates) :-
    findall(I2-J2,
            (   member(DI, [-1, 0, 1]),
                member(DJ, [-1, 0, 1]),
                ( DI =\= 0 ; DJ =\= 0 ),
                I2 is I + DI, J2 is J + DJ,
                I2 >= 1, I2 =< N, J2 >= 1, J2 =< M
            ),
            Coordinates).

% cells_at(+Rows, +Coordinates, -Cells): the entries of the matrix at the given
% Row-Column pairs.
cells_at(Rows, Coordinates, Cells) :-
    maplist({Rows}/[I-J, Cell]>>(nth1(I, Rows, Row), nth1(J, Row, Cell)),
            Coordinates, Cells).

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
