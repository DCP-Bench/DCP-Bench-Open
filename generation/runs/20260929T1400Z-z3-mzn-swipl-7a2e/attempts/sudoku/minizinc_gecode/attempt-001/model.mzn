% Sudoku: complete a 9 x 9 grid so that every row, column and 3 x 3 box holds
% each of the digits 1..9 once, keeping the digits already given.
include "globals.mzn";

array[int, int] of int: input_grid;  % 0 marks an empty cell
int: n = card(index_set_1of2(input_grid));
int: box = 3;  % side of a box

% grid[r, c] = the digit in cell (r, c)
array[1..n, 1..n] of var 1..n: grid;

% the given digits stay
constraint forall(r, c in 1..n where input_grid[r, c] != 0) (grid[r, c] = input_grid[r, c]);

% each row holds different digits
constraint forall(r in 1..n) (all_different([grid[r, c] | c in 1..n]));
% each column holds different digits
constraint forall(c in 1..n) (all_different([grid[r, c] | r in 1..n]));
% each 3 x 3 box holds different digits
constraint forall(i, j in 0..n div box - 1) (
    all_different([grid[r, c] | r in i * box + 1..(i + 1) * box, c in j * box + 1..(j + 1) * box]));

solve satisfy;

output ["{\"grid\": [",
        join(", ", ["[" ++ join(", ", [show(grid[r, c]) | c in 1..n]) ++ "]" | r in 1..n]),
        "]}"];
