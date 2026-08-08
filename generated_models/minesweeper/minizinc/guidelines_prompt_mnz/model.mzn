
% Minesweeper solver: determine which 'X' cells contain mines
include "globals.mzn";

int: n = 8;
int: X = -1;

% Input board: -1 = unopened (unknown), 0-8 = number of adjacent mines
array[1..n, 1..n] of int: game_data = 
[
    | 2, 3, X, 2, 2, X, 2, 1
    | X, X, 4, X, X, 4, X, 2
    | X, X, X, X, X, X, 4, X
    | X, 5, X, 6, X, X, X, 2
    | 2, X, X, X, 5, 5, X, 2
    | 1, 3, 4, X, X, X, 4, X
    | 0, 1, X, 4, X, X, X, 3
    | 0, 1, 2, X, 2, 3, X, 2
];

% Decision variables: 1 if there's a mine, 0 otherwise
array[1..n, 1..n] of var 0..1: mines;

% Open cells (0-8) cannot contain a mine
constraint
  forall(i, j in 1..n where game_data[i,j] >= 0) (
    mines[i,j] = 0
  );

% For each clue cell, the sum of adjacent mines equals the clue
constraint
  forall(i, j in 1..n where game_data[i,j] >= 0) (
    sum([
      mines[ii,jj] 
      | ii in max(1,i-1)..min(n,i+1),
        jj in max(1,j-1)..min(n,j+1),
        (ii != i \/ jj != j)
    ]) = game_data[i,j]
  );

solve satisfy;

% Output result as JSON with the key "mines"
output [
  "{",
    "\"mines\": [",
      join(
        ",",
        [ "[" ++ join(",", [ show(mines[i,j]) | j in 1..n ]) ++ "]"
          | i in 1..n
        ]
      ),
    "]",
  "}"
];
