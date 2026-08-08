
include "globals.mzn";

int: n = 9;
array[1..n, 1..n] of int: input_grid = [
    | 0, 0, 0,  2, 0, 5,  0, 0, 0
    | 0, 9, 0,  0, 0, 0,  7, 3, 0
    | 0, 0, 2,  0, 0, 9,  0, 6, 0
    | 2, 0, 0,  0, 0, 0,  4, 0, 9
    | 0, 0, 0,  0, 7, 0,  0, 0, 0
    | 6, 0, 9,  0, 0, 0,  0, 0, 1
    | 0, 8, 0,  4, 0, 0,  1, 0, 0
    | 0, 6, 3,  0, 0, 0,  0, 8, 0
    | 0, 0, 0,  6, 0, 8,  0, 0, 0
];

array[1..n, 1..n] of var 1..9: grid;

% Enforce the given clues
constraint
  forall(r in 1..n, c in 1..n) (
    if input_grid[r,c] != 0 then
      grid[r,c] = input_grid[r,c]
    else
      true
    endif
  );

% All rows contain distinct values
constraint
  forall(r in 1..n) (
    all_different([ grid[r,c] | c in 1..n ])
  );

% All columns contain distinct values
constraint
  forall(c in 1..n) (
    all_different([ grid[r,c] | r in 1..n ])
  );

% All 3x3 blocks contain distinct values
constraint
  forall(br in 0..2, bc in 0..2) (
    all_different([ grid[br*3 + rr, bc*3 + cc] | rr in 1..3, cc in 1..3 ])
  );

solve satisfy;

output [
  "{",
    "\"grid\":[" ++
      join(",", [
        "[" ++ join(",", [ show(grid[r,c]) | c in 1..n ]) ++ "]"
        | r in 1..n
      ])
      ++ "]",
  "}"
];
