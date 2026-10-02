% Knight's tour: move a knight over an n x n chessboard so that it visits every
% square exactly once and does not have to return to its start (an open tour).
% The board shows the number of the move (0 .. n*n-1) at which each square is visited.
include "globals.mzn";

int: n;  % size of the chessboard

int: squares = n * n;
set of int: Squares = 1..squares;   % squares numbered row by row: (row-1)*n + column

% The eight knight moves (a fact of chess, not of the instance).
array[1..8] of int: move_row = [2, 2, -2, -2, 1, 1, -1, -1];
array[1..8] of int: move_col = [1, -1, 1, -1, 2, -2, 2, -2];

% reachable[s] = the squares a knight can jump to from square s without leaving the board
array[Squares] of set of int: reachable =
    [ { (i + move_row[m] - 1) * n + (j + move_col[m])
      | m in 1..8 where i + move_row[m] in 1..n /\ j + move_col[m] in 1..n }
    | i in 1..n, j in 1..n ];

% all (from, to) pairs of squares that are one knight move apart, one per row
array[int] of int: jump_list = [ e | s in Squares, t in reachable[s], e in [s, t] ];
int: n_jumps = length(jump_list) div 2;
array[1..n_jumps, 1..2] of int: jumps = array2d(1..n_jumps, 1..2, jump_list);

% tour[k] = the square the knight is on after k-1 moves (tour[1] is where it starts)
array[Squares] of var Squares: tour;

% every square is visited exactly once
constraint all_different(tour);

% each move is a knight jump from the square before to the square after
constraint forall(k in 1..squares - 1) (table([tour[k], tour[k + 1]], jumps));

% place[s] = the number of the move (from 1) at which square s is visited, i.e. the
% position of s in the tour; it is the inverse of tour, so it
% adds no freedom of its own
array[Squares] of var Squares: place;
constraint inverse(tour, place);

% the board as the problem reports it, row by row
array[1..n, 1..n] of var 0..squares - 1: x;
constraint forall(i in 1..n, j in 1..n) (x[i, j] = place[(i - 1) * n + j] - 1);

solve satisfy;

output ["{\"x\": [", join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in 1..n]) ++ "]" | i in 1..n]), "]}"];
