:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Heterosquare of order n: fill an n x n square with the distinct integers
% 1..n^2 so that the sums of the rows, the columns and the two diagonals are
% all different.
model(Instance, Cells, [x-Rows]) :-
    N = Instance.n,                         % order of the square
    Max is N * N,                           % the entries are 1..n^2
    Cube is N * N * N,                      % bound the reference puts on a sum

    % Rows[i][j] is the integer in row i, column j.
    length(Rows, N),
    maplist({N, Max}/[Row]>>(length(Row, N), Row ins 1..Max), Rows),
    append(Rows, Cells),
    % all the entries are different
    all_distinct(Cells),

    % the lines whose sums must differ: rows, columns and both diagonals
    transpose(Rows, Columns),
    diagonal(Rows, 1, Diagonal),
    maplist(reverse, Rows, Mirrored),
    diagonal(Mirrored, 1, AntiDiagonal),
    append([Rows, Columns, [Diagonal, AntiDiagonal]], Lines),

    % the sum of every line, and all of these sums are different
    maplist({Cube}/[Line, Sum]>>(Sum in 1..Cube, sum(Line, #=, Sum)), Lines, Sums),
    all_distinct(Sums).

% diagonal(+Rows, +Index, -Cells): the entry in column Index of the first row,
% column Index+1 of the second row, and so on down the square.
diagonal([], _, []).
diagonal([Row|Rows], Index, [Cell|Cells]) :-
    nth1(Index, Row, Cell),
    Next is Index + 1,
    diagonal(Rows, Next, Cells).
