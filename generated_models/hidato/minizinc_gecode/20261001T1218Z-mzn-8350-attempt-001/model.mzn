% Hidato: a grid is partly filled with numbers. Fill the empty cells with the
% remaining numbers 1..(rows*columns), each used once, so that consecutive
% numbers sit in cells that touch horizontally, vertically or diagonally.
include "globals.mzn";

array[int, int] of int: puzzle;  % given numbers, 0 = empty cell to be filled

set of int: Rows = index_set_1of2(puzzle);
set of int: Cols = index_set_2of2(puzzle);
int: r = card(Rows);
int: c = card(Cols);
int: cells = r * c;

% x[i, j] = the number written in the cell in row i, column j
array[Rows, Cols] of var 1..cells: x;

% every number appears exactly once
constraint all_different(x);

% the given numbers are kept
constraint forall(i in Rows, j in Cols where puzzle[i, j] > 0) (x[i, j] = puzzle[i, j]);

% Where each number sits: place[k] is the cell (counted row by row from 1)
% holding the number k, and place_row[k], place_col[k] are its row and column
% (counted from 0). They are the inverse of x, so they add no freedom to it.
array[1..cells] of var 1..cells: place;
array[1..cells] of var 0..r - 1: place_row;
array[1..cells] of var 0..c - 1: place_col;
constraint inverse([x[i, j] | i in Rows, j in Cols], place);
constraint forall(k in 1..cells) (place[k] = place_row[k] * c + place_col[k] + 1);

% consecutive numbers k and k+1 are in cells that touch (one step or less in
% each direction); they are different cells because the numbers are all different
constraint forall(k in 1..cells - 1)
    (abs(place_row[k] - place_row[k + 1]) <= 1 /\ abs(place_col[k] - place_col[k + 1]) <= 1);

solve satisfy;

output ["{\"x\": [", join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in Cols]) ++ "]" | i in Rows]), "]}"];
