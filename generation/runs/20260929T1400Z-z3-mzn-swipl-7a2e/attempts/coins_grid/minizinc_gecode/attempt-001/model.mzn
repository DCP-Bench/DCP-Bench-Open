% Coins grid: place coins on an n x n grid, at most one per cell and exactly c
% in every row and every column, so that the sum of the squared distances of
% the coins from the main diagonal is as small as possible.
include "globals.mzn";

int: n;  % side of the grid
int: c;  % coins in each row and column

% x[i, j] = 1 if there is a coin in cell (i, j); this also gives at most one coin per cell
array[1..n, 1..n] of var 0..1: x;

% exactly c coins in every row
constraint forall(i in 1..n) (sum(j in 1..n) (x[i, j]) = c);
% exactly c coins in every column
constraint forall(j in 1..n) (sum(i in 1..n) (x[i, j]) = c);

% z = sum over coins of the squared horizontal distance to the diagonal,
% (i - j) ^ 2 for a coin in cell (i, j)
var int: z = sum(i in 1..n, j in 1..n) (x[i, j] * (i - j) * (i - j));
var int: objective = z;
solve minimize objective;

output ["{\"x\": [",
        join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in 1..n]) ++ "]" | i in 1..n]),
        "], \"z\": ", show(z), "}"];
