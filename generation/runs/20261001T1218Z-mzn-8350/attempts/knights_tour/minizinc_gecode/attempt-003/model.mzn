% Knight's tour: move a knight over an n x n chessboard so that it visits every
% square exactly once and does not have to return to its start (an open tour).
% The board shows the number of the move (0 .. n*n-1) at which each square is visited.
include "globals.mzn";

int: n;  % size of the chessboard

int: squares = n * n;
set of int: Squares = 1..squares;   % squares numbered row by row: (row-1)*n + column
int: end_mark = squares + 1;        % extra node standing for "the tour is over"

% The eight knight moves (a fact of chess, not of the instance).
array[1..8] of int: move_row = [2, 2, -2, -2, 1, 1, -1, -1];
array[1..8] of int: move_col = [1, -1, 1, -1, 2, -2, 2, -2];

% moves[s] = the squares a knight can jump to from square s without leaving the board
array[Squares] of set of int: moves =
    [ { (i + move_row[m] - 1) * n + (j + move_col[m])
      | m in 1..8 where i + move_row[m] in 1..n /\ j + move_col[m] in 1..n }
    | i in 1..n, j in 1..n ];

% A tour is a path through all squares. It is written as the square the knight
% goes to next (next_square[s]), where the last square points to the extra
% node, and the extra node points to the first square. Then the tour is a
% single cycle through all squares and the extra node. This form is used because
% the numbers on the board are then fixed by the path and are found by propagation,
% instead of being searched square by square.
array[1..end_mark] of var 1..end_mark: next_square;
constraint circuit(next_square);

% every square is followed by a knight move or by the end of the tour
constraint forall(s in Squares) (next_square[s] in moves[s] union {end_mark});

% move_number[s] = at which move the knight is on square s (the first square is move 0);
% the extra node counts as move -1, so that the first square gets 0
array[1..end_mark] of var -1..squares - 1: move_number;
constraint move_number[end_mark] = -1;

% every move goes one number higher than the one before it (the end of the tour
% sets no number); from the extra node the first square gets the number 0
constraint forall(s in 1..end_mark)
    (next_square[s] = end_mark \/ move_number[next_square[s]] = move_number[s] + 1);

% each square is visited exactly once (implied by the path, helps propagation)
constraint all_different(move_number);

% the board as the problem reports it, row by row
array[1..n, 1..n] of var 0..squares - 1: x;
constraint forall(i in 1..n, j in 1..n) (x[i, j] = move_number[(i - 1) * n + j]);

solve satisfy;

output ["{\"x\": [", join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in 1..n]) ++ "]" | i in 1..n]), "]}"];
