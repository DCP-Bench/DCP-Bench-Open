:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Coins grid: place coins on an n x n grid, at most one per cell and exactly c
% in every row and every column, so that the sum of the squared distances of
% the coins from the main diagonal is as small as possible.
model(Instance, Vars, [x-Rows, z-Z], min(Z)) :-
    N = Instance.n,     % side of the grid
    C = Instance.c,     % coins in each row and column

    % Rows[i][j] = 1 if there is a coin in cell (i, j); this also gives at most one coin per cell
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Rows),

    % exactly c coins in every row
    maplist({C}/[Row]>>sum(Row, #=, C), Rows),
    % exactly c coins in every column
    transpose(Rows, Columns),
    maplist({C}/[Column]>>sum(Column, #=, C), Columns),

    % z = sum over coins of the squared horizontal distance to the diagonal,
    % (i - j) ^ 2 for a coin in cell (i, j)
    findall(W, (between(1, N, I), between(1, N, J), W is (I - J) * (I - J)), Weights),
    append(Rows, Cells),
    Bound is N * N * (N - 1) * (N - 1),
    Z in 0..Bound,
    scalar_product(Weights, Cells, #=, Z),
    append(Cells, [Z], Vars).
