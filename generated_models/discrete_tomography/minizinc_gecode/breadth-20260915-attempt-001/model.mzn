include "globals.mzn";

array[int] of int: row_sums;
array[int] of int: col_sums;

set of int: Rows = index_set(row_sums);
set of int: Columns = index_set(col_sums);
array[Rows, Columns] of var 0..1: x;

constraint forall(i in Rows) (sum(j in Columns) (x[i, j]) = row_sums[i]);
constraint forall(j in Columns) (sum(i in Rows) (x[i, j]) = col_sums[j]);

solve satisfy;

output ["{\"matrix\": [",
        join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in Columns]) ++ "]" | i in Rows]),
        "]}"];
