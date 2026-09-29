% Maximum density still life: on an n x m active area of Conway's Game of Life,
% find the pattern with the most live cells that is stable (unchanged in the
% next generation). Cells outside the area are dead but still obey the rules.
include "globals.mzn";

int: n;  % rows of the active area
int: m;  % columns of the active area

% grid[i, j] is true when the cell is alive
array[1..n, 1..m] of var bool: grid;

% cells inside the area stay as they are
constraint forall(i in 1..n, j in 1..m) (
    let { var int: count = sum(a in max(1, i - 1)..min(n, i + 1), b in max(1, j - 1)..min(m, j + 1)
                               where not (a = i /\ b = j)) (bool2int(grid[a, b])) } in
    % a live cell survives only with 2 or 3 live neighbours
    (grid[i, j] -> (count >= 2 /\ count <= 3)) /\
    % a dead cell must not have exactly 3 live neighbours, or it would be born
    (not grid[i, j] -> count != 3));

% dead cells just outside the area must not be born either. The cells that touch
% the area along its top and bottom edges see three cells of the first / last row,
% those along the left and right edges three cells of the first / last column; the
% four outer corners see one cell and never reach 3.
constraint forall(j in 1..m) (
    sum(a in max(1, j - 1)..min(m, j + 1)) (bool2int(grid[1, a])) != 3 /\
    sum(a in max(1, j - 1)..min(m, j + 1)) (bool2int(grid[n, a])) != 3);
constraint forall(i in 1..n) (
    sum(a in max(1, i - 1)..min(n, i + 1)) (bool2int(grid[a, 1])) != 3 /\
    sum(a in max(1, i - 1)..min(n, i + 1)) (bool2int(grid[a, m])) != 3);

% maximise the number of live cells
var int: objective = sum(i in 1..n, j in 1..m) (bool2int(grid[i, j]));
solve maximize objective;

output ["{\"grid\": [",
        join(", ", ["[" ++ join(", ", [show(grid[i, j]) | j in 1..m]) ++ "]" | i in 1..n]),
        "]}"];
