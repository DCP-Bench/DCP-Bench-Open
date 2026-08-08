include "globals.mzn";

% Input data
array[1..9, 1..9] of int: input_grid = [
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

% Decision variables: the solved Sudoku grid
array[1..9, 1..9] of var 1..9: grid;

% Constraints

% 1. Cells with given numbers must be equal to those numbers
constraint
    forall(r in 1..9, c in 1..9) (
        if input_grid[r,c] != 0 then
            grid[r,c] = input_grid[r,c]
        else
            true
        endif
    );

% 2. All rows contain distinct numbers
constraint
    forall(r in 1..9) (
        alldifferent([grid[r,c] | c in 1..9])
    );

% 3. All columns contain distinct numbers
constraint
    forall(c in 1..9) (
        alldifferent([grid[r,c] | r in 1..9])
    );

% 4. All 3x3 blocks contain distinct numbers
constraint
    forall(br in 0..2, bc in 0..2) (
        alldifferent([grid[3*br + rr, 3*bc + cc] | rr in 1..3, cc in 1..3])
    );

solve satisfy;

output [
    "{",
    "\"grid\": [",
    join(",\n", [
        "[" ++ join(", ", [show(grid[r,c]) | c in 1..9]) ++ "]"
        | r in 1..9
    ]),
    "]",
    "}"
];