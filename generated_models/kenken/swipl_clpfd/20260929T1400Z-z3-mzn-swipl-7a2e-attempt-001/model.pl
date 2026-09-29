:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% KenKen: fill an n x n grid with 1..n so that each row and column holds every
% digit once, and each cage of cells achieves its target. A cage of two cells
% reaches it by a sum, product, difference or quotient; a larger cage by its sum
% or its product. Digits may repeat inside a cage.
model(Instance, Vars, [x-Rows]) :-
    N = Instance.n,
    Cages = Instance.problem,   % [Target, [[Row, Column], ...]] with cells counted from 1

    % Rows[r][c] = the digit in cell (r, c)
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 1..N), Rows),

    % each row and each column holds different digits
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),

    maplist({Rows}/[[Target, Cells]]>>(
                maplist({Rows}/[[R, C], Cell]>>(nth1(R, Rows, Row), nth1(C, Row, Cell)), Cells, Cage),
                cage(Cage, Target)), Cages),
    append(Rows, Vars).

% cage(+Cells, +Target): the cage reaches its target
cage([A, B], Target) :- !,
    % two cells reach it by a sum, product, quotient (either way round) or difference (either way round)
    (A + B #= Target) #\/ (A * B #= Target) #\/ (A * Target #= B) #\/ (B * Target #= A)
    #\/ (A - B #= Target) #\/ (B - A #= Target).
cage(Cells, Target) :-
    % a larger cage adds up to the target or multiplies to it
    foldl([Cell, Before, After]>>(After #= Before * Cell), Cells, 1, Product),
    sum(Cells, #=, Sum),
    (Sum #= Target) #\/ (Product #= Target).
