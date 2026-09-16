% Heterosquare: an n by n square of the distinct integers 1..n^2 whose row,
% column and diagonal sums are all different from each other.
include "globals.mzn";

int: n;

array[1..n, 1..n] of var 1..n*n: x;
array[1..n] of var 1..n*n*n: row_sums;
array[1..n] of var 1..n*n*n: col_sums;
var 1..n*n*n: diag1;
var 1..n*n*n: diag2;

constraint all_different([x[i, j] | i in 1..n, j in 1..n]);

constraint forall(i in 1..n) (row_sums[i] = sum(j in 1..n) (x[i, j]));
constraint forall(j in 1..n) (col_sums[j] = sum(i in 1..n) (x[i, j]));
constraint diag1 = sum(i in 1..n) (x[i, i]);
constraint diag2 = sum(i in 1..n) (x[i, n - i + 1]);

constraint all_different(row_sums ++ col_sums ++ [diag1, diag2]);

solve satisfy;

output ["{\"x\": [",
        join(", ", [ "[" ++ join(", ", [show(x[i, j]) | j in 1..n]) ++ "]"
                   | i in 1..n ]),
        "]}"];
