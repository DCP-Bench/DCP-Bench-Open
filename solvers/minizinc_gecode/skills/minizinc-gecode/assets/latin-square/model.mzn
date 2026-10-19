% Latin square: an n x n grid in which every row and every column
% holds each value 1..n exactly once. The order and the first row
% come from data.dzn; the solver finds the other rows.
include "globals.mzn";

int: n;
array[1..n] of 1..n: first_row;
array[1..n, 1..n] of var 1..n: sq;

constraint forall(j in 1..n)(sq[1, j] = first_row[j]);
constraint forall(i in 1..n)(all_different([sq[i, j] | j in 1..n]));
constraint forall(j in 1..n)(all_different([sq[i, j] | i in 1..n]));

solve satisfy;

output [ "row " ++ show(i) ++ ": " ++ show([sq[i, j] | j in 1..n]) ++ "\n" | i in 1..n ];
