% Quasigroup completion: fill the empty cells of a partially filled N x N grid
% so that every row and every column contains each of 1..N exactly once (a
% Latin square).
include "globals.mzn";

int: N;  % size of the square
array[1..N, 1..N] of int: start;  % given cells; 0 marks an empty cell

% puzzle[i, j] = the number in cell (i, j), from 1 to N
array[1..N, 1..N] of var 1..N: puzzle;

% the given cells keep their value
constraint forall(i, j in 1..N where start[i, j] != 0) (puzzle[i, j] = start[i, j]);

% each row holds different numbers
constraint forall(i in 1..N) (all_different([puzzle[i, j] | j in 1..N]));
% each column holds different numbers
constraint forall(j in 1..N) (all_different([puzzle[i, j] | i in 1..N]));

solve satisfy;

output ["{\"puzzle\": [",
        join(", ", ["[" ++ join(", ", [show(puzzle[i, j]) | j in 1..N]) ++ "]" | i in 1..N]),
        "]}"];
