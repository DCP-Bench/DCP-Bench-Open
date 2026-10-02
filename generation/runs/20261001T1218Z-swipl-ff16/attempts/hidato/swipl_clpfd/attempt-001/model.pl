:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Hidato: a grid is partly filled with numbers. Fill the empty cells with the
% numbers 1..(rows * columns), each used once, so that consecutive numbers sit
% in cells that touch horizontally, vertically or diagonally.
model(Instance, Positions, [x-Rows]) :-
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

    % Positions[k] is the cell (numbered row by row from 1) that holds number k.
    % This is the same assignment seen from the numbers' side: it makes
    % "consecutive numbers touch" a constraint on two neighbouring entries
    % instead of a search for where a number is written.
    length(Positions, Total),
    Positions ins 1..Total,
    all_distinct(Positions),
    numlist(1, Total, Numbers),
    maplist({Cells}/[Number, Position]>>element(Position, Cells, Number), Numbers, Positions),

    % number k+1 sits in a cell touching the cell of number k (a cell never
    % touches itself)
    touching_cells(R, C, Touching),
    consecutive(Positions, Pairs),
    tuples_in(Pairs, Touching).

% touching_cells(+R, +C, -Pairs): every [A, B] where cells A and B of an R x C
% grid, numbered row by row from 1, touch horizontally, vertically or
% diagonally.
touching_cells(R, C, Pairs) :-
    findall([A, B],
            (   between(1, R, I), between(1, C, J),
                between(-1, 1, DI), between(-1, 1, DJ),
                ( DI =\= 0 ; DJ =\= 0 ),
                I2 is I + DI, J2 is J + DJ,
                I2 >= 1, I2 =< R, J2 >= 1, J2 =< C,
                A is (I - 1) * C + J,
                B is (I2 - 1) * C + J2
            ),
            Pairs).

% consecutive(+List, -Pairs): the pairs [X, Y] of neighbours in List.
consecutive([_], []) :- !.
consecutive([X, Y|Rest], [[X, Y]|Pairs]) :-
    consecutive([Y|Rest], Pairs).
