% Nonogram (csplib_012): shade cells of an R x C grid so that the runs of shaded
% squares in every row and every column give that line's clue, in order.

:- lib(ic).
:- lib(lists).
:- lib(listut).

% The instance gives rows, cols, row_rules (one clue per row) and col_rules
% (one clue per column). Clues are padded with leading 0s; the 0s are dropped.
model(Instance, Vars, [board-Board]) :-
    memberchk(rows-R, Instance),
    memberchk(cols-C, Instance),
    memberchk(row_rules-RowRules, Instance),
    memberchk(col_rules-ColRules, Instance),
    % board[i][j] = 1 if the square in row i, column j is shaded
    length(Board, R),
    ( foreach(Row, Board), param(C) do
        length(Row, C),
        Row :: 0..1
    ),
    % each row: its blocks, in order, are the shaded runs of the row
    ( foreach(Row, Board), foreach(Clue, RowRules), foreach(Sts, RowStarts) do
        line_clue(Row, Clue, Sts)
    ),
    % each column: its blocks, in order, are the shaded runs of the column
    transpose_board(Board, Cols),
    ( foreach(Col, Cols), foreach(Clue, ColRules), foreach(Sts, ColStarts) do
        line_clue(Col, Clue, Sts)
    ),
    flatten(Board, BoardVars),
    flatten(RowStarts, RowStartVars),
    flatten(ColStarts, ColStartVars),
    append(BoardVars, RowStartVars, V1),
    append(V1, ColStartVars, Vars).

% Search: smallest domain first. The default labelling in input order is slow on
% the larger grids.
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% A line of cells whose shaded runs are exactly the blocks of Clue, in order.
% Starts are the first square of each block; they are auxiliary variables.
line_clue(Cells, Clue, Starts) :-
    nonzero(Clue, Blocks),
    length(Cells, N),
    length(Blocks, K),
    length(Starts, K),
    (   K == 0
    ->  ( foreach(X, Cells) do X #= 0 )
    ;   Starts :: 1..N,
        place(Starts, Blocks, N),
        post_cells(Cells, 1, Starts, Blocks)
    ).

% Blocks are placed left to right with at least one unshaded square between them,
% and each block fits inside the line.
place([S], [B], N) :-
    S #=< N - B + 1.
place([S1, S2 | Ss], [B1 | Bs], N) :-
    S1 #=< N - B1 + 1,
    S2 #>= S1 + B1 + 1,
    place([S2 | Ss], Bs, N).

% A square is shaded exactly when it lies inside one of the blocks.
post_cells([], _, _, _).
post_cells([X | Xs], J, Starts, Blocks) :-
    cover(Starts, Blocks, J, Ins),
    X #= sum(Ins),
    J1 is J + 1,
    post_cells(Xs, J1, Starts, Blocks).

% In[k] = 1 if square J lies in block k, which starts at S and has length B.
cover([], [], _, []).
cover([S | Ss], [B | Bs], J, [In | Ins]) :-
    In #= (S #=< J and S + B #> J),
    cover(Ss, Bs, J, Ins).

% The non-zero entries of a clue, in order.
nonzero([], []).
nonzero([X | Xs], Ys) :-
    (   X =:= 0
    ->  Ys = Ys1
    ;   Ys = [X | Ys1]
    ),
    nonzero(Xs, Ys1).

% Rows to columns.
transpose_board([[] | _], []) :- !.
transpose_board(Rows, [Col | Cols]) :-
    first_column(Rows, Col, Rest),
    transpose_board(Rest, Cols).

first_column([], [], []).
first_column([[H | T] | Rs], [H | Hs], [T | Ts]) :-
    first_column(Rs, Hs, Ts).
