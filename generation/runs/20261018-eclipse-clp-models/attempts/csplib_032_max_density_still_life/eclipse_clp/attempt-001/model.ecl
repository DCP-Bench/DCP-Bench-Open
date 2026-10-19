% Maximum density still life on an n x m active grid (Conway's Game of Life).
% A still life is a pattern that does not change from one generation to the next.
% Cells outside the active grid are dead. Maximise the number of live cells.
:- lib(ic).
:- lib(listut).

% The board is the active grid padded with one ring of dead cells, so the
% neighbours of the active cells, and the dead cells just outside the grid, are
% all in the board.
model(Instance, Vars, [grid-Rows], max(sum(Vars))) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    NP is N + 2,
    MP is M + 2,
    board(NP, MP, P),
    % the ring of cells outside the active grid is dead
    ( for(I, 1, NP), param(P, NP, MP) do
        ( for(J, 1, MP), param(P, I, NP, MP) do
            ( (I =:= 1 ; I =:= NP ; J =:= 1 ; J =:= MP) ->
                cell(P, I, J, V), V #= 0
            ;   true
            )
        )
    ),
    % a live cell has 2 or 3 live neighbours; a dead cell does not have exactly 3
    % live neighbours (dead cells just outside the active grid included)
    ( for(I, 1, NP), param(P, NP, MP) do
        ( for(J, 1, MP), param(P, I, NP, MP) do
            still_life_rule(P, I, J, NP, MP)
        )
    ),
    % the active grid is the inner n x m part of the board
    N1 is N + 1,
    M1 is M + 1,
    ( for(I, 2, N1), foreach(Row, Rows), param(P, M1) do
        ( for(J, 2, M1), foreach(V, Row), param(P, I) do
            cell(P, I, J, V)
        )
    ),
    flatten(Rows, Vars).

% board(+Rows, +Cols, -P): a Rows x Cols list of rows of 0/1 variables
board(NP, MP, P) :-
    length(P, NP),
    ( foreach(Row, P), param(MP) do
        length(Row, MP),
        Row :: 0..1
    ).

cell(P, I, J, V) :-
    nth1(I, P, Row),
    nth1(J, Row, V).

% cells outside the board are dead
cell_or_zero(P, NP, MP, I, J, V) :-
    (   I >= 1, I =< NP, J >= 1, J =< MP
    ->  cell(P, I, J, V)
    ;   V = 0
    ).

% the eight neighbours of cell (I, J) and the still life rule for it
still_life_rule(P, I, J, NP, MP) :-
    cell(P, I, J, V),
    Offsets = [-1-(-1), -1-0, -1-1, 0-(-1), 0-1, 1-(-1), 1-0, 1-1],
    ( foreach(DI-DJ, Offsets), foreach(W, Ns), param(P, I, J, NP, MP) do
        I2 is I + DI,
        J2 is J + DJ,
        cell_or_zero(P, NP, MP, I2, J2, W)
    ),
    S #= sum(Ns),
    % a live cell must have exactly 2 or 3 live neighbours
    (V #= 1) => (S #>= 2 and S #=< 3),
    % a dead cell must not have exactly 3 live neighbours
    (V #= 0) => (S #\= 3).
