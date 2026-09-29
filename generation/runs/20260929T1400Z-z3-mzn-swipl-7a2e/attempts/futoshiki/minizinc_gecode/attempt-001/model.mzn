% Futoshiki: fill an n x n grid with 1..n so that every row and column has each
% number once, some cells are given, and the listed "less than" signs between
% neighbouring cells hold.
include "globals.mzn";

array[int, int] of int: values;  % given cells; 0 means empty
array[int, int] of int: lt;      % [i1, j1, i2, j2]: cell (i1, j1) must be smaller than cell (i2, j2)

int: size = card(index_set_1of2(values));

array[1..size, 1..size] of var 1..size: grid;

% the given numbers are fixed
constraint forall(r, c in 1..size where values[r, c] > 0) (grid[r, c] = values[r, c]);

% every row holds different numbers
constraint forall(r in 1..size) (all_different([grid[r, c] | c in 1..size]));
% every column holds different numbers
constraint forall(c in 1..size) (all_different([grid[r, c] | r in 1..size]));

% each inequality sign: the first cell is smaller than the second (the
% coordinates in the data start at 1, as MiniZinc indices do)
constraint forall(k in index_set_1of2(lt)) (grid[lt[k, 1], lt[k, 2]] < grid[lt[k, 3], lt[k, 4]]);

solve satisfy;

output ["{\"grid\": [",
        join(", ", ["[" ++ join(", ", [show(grid[r, c]) | c in 1..size]) ++ "]" | r in 1..size]),
        "]}"];
