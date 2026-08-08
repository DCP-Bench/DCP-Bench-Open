include "globals.mzn";

% Input data
int: rows = 8;
int: cols = 8;
int: X = -1;

array[1..rows, 1..cols] of int: game_data = [
    | 2, 3, X, 2, 2, X, 2, 1
    | X, X, 4, X, X, 4, X, 2
    | X, X, X, X, X, X, 4, X
    | X, 5, X, 6, X, X, X, 2
    | 2, X, X, X, 5, 5, X, 2
    | 1, 3, 4, X, X, X, 4, X
    | 0, 1, X, 4, X, X, X, 3
    | 0, 1, 2, X, 2, 3, X, 2
];

% Decision variables
% mines[r,c] = 1 if cell (r,c) contains a mine, 0 otherwise
array[1..rows, 1..cols] of var 0..1: mines;

% Constraints
% For cells that are opened (game_data[r,c] != X), the number must equal the count of mines in adjacent cells
constraint
    forall(r in 1..rows, c in 1..cols where game_data[r,c] != X) (
        let {
            % Define the neighbors coordinates within bounds
            array[int] of int: dr = [-1,-1,-1,0,0,1,1,1],
            array[int] of int: dc = [-1,0,1,-1,1,-1,0,1],
            array[int] of int: nbrs = [ (nr, nc) | i in 1..8 where
                let {int: nr = r + dr[i], int: nc = c + dc[i]} in
                nr >= 1 /\ nr <= rows /\ nc >= 1 /\ nc <= cols
            ]
        } in
        sum([mines[nr,nc] | (nr,nc) in nbrs]) == game_data[r,c]
    );

% For cells that are opened (game_data[r,c] != X), they cannot be mines
constraint
    forall(r in 1..rows, c in 1..cols where game_data[r,c] != X) (
        mines[r,c] == 0
    );

solve satisfy;

output [
    "{",
    "\"mines\": [",
    join(",\n", [
        "[" ++ join(", ", [show(mines[r,c]) | c in 1..cols]) ++ "]"
        | r in 1..rows
    ]),
    "]",
    "}"
];