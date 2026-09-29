% Flip rows and columns (Einav's puzzle): choose, for every row and column,
% whether to flip its sign so that every row sum and every column sum is
% non-negative, with the smallest possible total of the whole matrix.
include "globals.mzn";

array[int, int] of int: input_matrix;

set of int: Rows = index_set_1of2(input_matrix);
set of int: Columns = index_set_2of2(input_matrix);

% the signs of the rows and columns: -1 (flipped) or +1, never 0
array[Rows] of var {-1, 1}: row_signs;
array[Columns] of var {-1, 1}: col_signs;

% x[i, j] = input value after both flips
array[Rows, Columns] of var -100..100: x;
constraint forall(i in Rows, j in Columns) (x[i, j] = input_matrix[i, j] * row_signs[i] * col_signs[j]);

% every row and column sums to at least 0; the reference's declared
% domain for a sum is 0..300, which is mirrored here
constraint forall(i in Rows) (sum(j in Columns) (x[i, j]) in 0..300);
constraint forall(j in Columns) (sum(i in Rows) (x[i, j]) in 0..300);

% total sum of the flipped matrix, to be minimised (declared range 0..1000)
var 0..1000: total_sum = sum(i in Rows, j in Columns) (x[i, j]);
var int: objective = total_sum;
solve minimize objective;

output ["{\"row_signs\": [", join(", ", [show(row_signs[i]) | i in Rows]),
        "], \"col_signs\": [", join(", ", [show(col_signs[j]) | j in Columns]), "]}"];
