% Magic square: fill an n x n grid with the different integers 1..n^2 so that
% every row, every column and both diagonals add up to the same sum.
include "globals.mzn";

int: n;  % side of the square
int: magic_sum = n * (n * n + 1) div 2;  % the sum every line has to reach

% square[i, j] = the number in cell (i, j)
array[1..n, 1..n] of var 1..n * n: square;

% all numbers are different
constraint all_different([square[i, j] | i, j in 1..n]);

% each row adds up to the magic sum
constraint forall(i in 1..n) (sum(j in 1..n) (square[i, j]) = magic_sum);
% each column adds up to the magic sum
constraint forall(j in 1..n) (sum(i in 1..n) (square[i, j]) = magic_sum);
% the main diagonal adds up to the magic sum
constraint sum(i in 1..n) (square[i, i]) = magic_sum;
% the other diagonal adds up to the magic sum
constraint sum(i in 1..n) (square[i, n + 1 - i]) = magic_sum;

solve satisfy;

output ["{\"square\": [",
        join(", ", ["[" ++ join(", ", [show(square[i, j]) | j in 1..n]) ++ "]" | i in 1..n]),
        "]}"];
