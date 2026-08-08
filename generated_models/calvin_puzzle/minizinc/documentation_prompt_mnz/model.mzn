include "globals.mzn";

% Input data
int: n = 5;

% The grid positions are indexed from 1 to n in both dimensions
set of int: ROWS = 1..n;
set of int: COLS = 1..n;

% Total number of cells
int: N = n * n;

% Decision variables:
% x[i,j] = the number placed at position (i,j), from 1 to N
array[ROWS, COLS] of var 1..N: x;

% pos[num] = (row, col) position of the number num in the grid
array[1..N] of var ROWS: pos_row;
array[1..N] of var COLS: pos_col;

% Constraints:

% 1) All numbers from 1 to N appear exactly once in the grid
constraint
  alldifferent([x[i,j] | i,j in ROWS, COLS]);

% 2) Link positions and grid values:
% For each cell (i,j), x[i,j] = k <-> pos_row[k] = i /\ pos_col[k] = j
% We enforce that for all k in 1..N, the position (pos_row[k], pos_col[k]) contains k
constraint
  forall(k in 1..N) (
    x[pos_row[k], pos_col[k]] = k
  );

% 3) Movement constraints between consecutive numbers k and k+1:
% If the move is vertical or horizontal, distance must be exactly 3 squares away (gap of 2)
% If the move is diagonal, distance must be exactly 2 squares away (gap of 1)
%
% Let dr = abs(pos_row[k+1] - pos_row[k])
% Let dc = abs(pos_col[k+1] - pos_col[k])
%
% Movement Type I (vertical/horizontal): (dr = 3 and dc = 0) or (dr = 0 and dc = 3)
% Movement Type II (diagonal): dr = 2 and dc = 2
%
% Exactly one of these must hold for each consecutive pair

constraint
  forall(k in 1..N-1) (
    let {
      var int: dr = abs(pos_row[k+1] - pos_row[k]),
      var int: dc = abs(pos_col[k+1] - pos_col[k])
    } in
      ( (dr = 3 /\ dc = 0) \/
        (dr = 0 /\ dc = 3) \/
        (dr = 2 /\ dc = 2)
      )
  );

% Solve: find any solution satisfying the constraints
solve satisfy;

% Output the completed grid x as a 2D array
output [
  "{\n",
  "  \"x\": [\n",
  join(",\n", [
    "    [" ++ join(", ", [show(x[i,j]) | j in COLS]) ++ "]"
    | i in ROWS
  ]),
  "\n  ]\n",
  "}"
];