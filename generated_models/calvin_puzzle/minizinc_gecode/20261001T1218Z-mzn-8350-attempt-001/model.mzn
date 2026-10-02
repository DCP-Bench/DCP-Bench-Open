% Calvin puzzle: fill an n x n grid with the numbers 1..n*n, each exactly once,
% so that every number is followed (n -> n+1) by the next one in a cell that is
% reached by one of two kinds of move: horizontally or vertically exactly three
% squares away (a gap of two squares), or diagonally exactly two squares away
% (a gap of one square).
include "globals.mzn";

int: n;  % size of the grid

int: squares = n * n;
set of int: Squares = 1..squares;   % cells numbered row by row: (row-1)*n + column
int: end_mark = squares + 1;        % extra node standing for "the sequence is over"

% The moves from one number to the next (fixed by the puzzle): 3 squares
% horizontally or vertically, or 2 squares in both directions (diagonal).
array[1..8] of int: move_row = [3, -3, 0, 0, 2, 2, -2, -2];
array[1..8] of int: move_col = [0, 0, 3, -3, 2, -2, 2, -2];

% moves[s] = the cells that can follow cell s, i.e. reached by a move that stays inside the grid
array[Squares] of set of int: moves =
    [ { (i + move_row[m] - 1) * n + (j + move_col[m])
      | m in 1..8 where i + move_row[m] in 1..n /\ j + move_col[m] in 1..n }
    | i in 1..n, j in 1..n ];

% The sequence 1, 2, ..., n*n is a path through all cells. It is written as the
% cell that holds the next number (next_cell[s]); the cell of the number n*n
% points to the extra node and the extra node points to the cell of number 1, so
% that the path is one cycle through all cells and the extra node. The numbers
% in the grid are then fixed by the path and found by propagation instead of
% being searched cell by cell.
array[1..end_mark] of var 1..end_mark: next_cell;
constraint circuit(next_cell);

% every cell is followed by a cell reached by a move, or by the end of the sequence
constraint forall(s in Squares) (next_cell[s] in moves[s] union {end_mark});

% number_in[s] = the number written in cell s; the extra node carries 0 so that
% the first cell gets 1
array[1..end_mark] of var 0..squares: number_in;
constraint number_in[end_mark] = 0;

% the cell that follows holds the next number: from the extra node to any cell
% (it holds 1), and from a cell to a cell that can follow it
function set of int: followers(int: s) = if s = end_mark then Squares else moves[s] endif;
constraint forall(s in 1..end_mark, t in followers(s))
    (next_cell[s] = t -> number_in[t] = number_in[s] + 1);

% each number is used exactly once (implied by the path, helps propagation)
constraint all_different(number_in);

% the grid as the puzzle reports it, row by row
array[1..n, 1..n] of var 1..squares: x;
constraint forall(i in 1..n, j in 1..n) (x[i, j] = number_in[(i - 1) * n + j]);

solve satisfy;

output ["{\"x\": [", join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in 1..n]) ++ "]" | i in 1..n]), "]}"];
