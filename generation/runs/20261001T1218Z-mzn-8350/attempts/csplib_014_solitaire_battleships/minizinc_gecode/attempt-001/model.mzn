% Solitaire battleships: fill a grid with water and the pieces of a fleet of
% ships (submarines of one square, longer ships made of two ends and middle
% squares), so that row and column totals are met, no two ships touch, and the
% given hints hold.
include "globals.mzn";

int: rows;
int: cols;
array[1..rows] of int: rowsum;   % number of occupied squares in each row
array[1..cols] of int: colsum;   % number of occupied squares in each column
array[int, 1..2] of int: fleet_counts;  % each row: [ship size, how many ships of that size]
array[int, 1..3] of int: hints;  % each row: [row, column, cell value] of a given square (counted from 0)

% The codes of the cell values are part of the instance (the instance also
% lists a code _SHIP = 1; it is not needed by the model).
int: WATER;
int: CIRCLE;   % a submarine, a ship of one square
int: LEFT;     % left end of a horizontal ship
int: RIGHT;    % right end of a horizontal ship
int: TOP;      % top end of a vertical ship
int: BOTTOM;   % bottom end of a vertical ship
int: MIDDLE;   % a square inside a ship of three or more squares

set of int: Rows = 0..rows - 1;
set of int: Cols = 0..cols - 1;

% grid[r, c] = the content of the square in row r, column c (both counted
% from 0). The reference lets each square take any code 0..7.
array[Rows, Cols] of var 0..7: grid;

% a position lies inside the grid
function bool: on_grid(int: r, int: c) = r >= 0 /\ r < rows /\ c >= 0 /\ c < cols;

% the square at (r, c) is water, or lies outside the grid
predicate water_or_edge(int: r, int: c) = if on_grid(r, c) then grid[r, c] = WATER else true endif;

% the square at (r, c) is inside the grid and holds one of the given pieces
predicate piece_at(int: r, int: c, set of int: pieces) = if on_grid(r, c) then grid[r, c] in pieces else false endif;

% the given squares (shots already taken) have the given content
constraint forall(h in index_set_1of2(hints)) (grid[hints[h, 1], hints[h, 2]] = hints[h, 3]);

% the number of occupied (non-water) squares in each row and each column
constraint forall(r in Rows) (sum(c in Cols) (bool2int(grid[r, c] > WATER)) = rowsum[r + 1]);
constraint forall(c in Cols) (sum(r in Rows) (bool2int(grid[r, c] > WATER)) = colsum[c + 1]);

% no ships touch, not even at a corner: next to every occupied square the four
% diagonal squares are water
constraint forall(r in Rows, c in Cols)
    (grid[r, c] > WATER -> (water_or_edge(r - 1, c - 1) /\ water_or_edge(r - 1, c + 1) /\
                            water_or_edge(r + 1, c - 1) /\ water_or_edge(r + 1, c + 1)));

% a submarine is surrounded by water on all four sides
constraint forall(r in Rows, c in Cols)
    (grid[r, c] = CIRCLE -> (water_or_edge(r - 1, c) /\ water_or_edge(r + 1, c) /\
                             water_or_edge(r, c - 1) /\ water_or_edge(r, c + 1)));

% the left end of a ship has a middle or right end to its right and water on its other three sides
constraint forall(r in Rows, c in Cols)
    (grid[r, c] = LEFT -> (piece_at(r, c + 1, {MIDDLE, RIGHT}) /\ water_or_edge(r, c - 1) /\
                           water_or_edge(r - 1, c) /\ water_or_edge(r + 1, c)));

% the right end of a ship has a middle or left end to its left and water on its other three sides
constraint forall(r in Rows, c in Cols)
    (grid[r, c] = RIGHT -> (piece_at(r, c - 1, {MIDDLE, LEFT}) /\ water_or_edge(r, c + 1) /\
                            water_or_edge(r - 1, c) /\ water_or_edge(r + 1, c)));

% the top end of a ship has a middle or bottom end below it and water on its other three sides
constraint forall(r in Rows, c in Cols)
    (grid[r, c] = TOP -> (piece_at(r + 1, c, {MIDDLE, BOTTOM}) /\ water_or_edge(r - 1, c) /\
                          water_or_edge(r, c - 1) /\ water_or_edge(r, c + 1)));

% the bottom end of a ship has a middle or top end above it and water on its other three sides
constraint forall(r in Rows, c in Cols)
    (grid[r, c] = BOTTOM -> (piece_at(r - 1, c, {MIDDLE, TOP}) /\ water_or_edge(r + 1, c) /\
                             water_or_edge(r, c - 1) /\ water_or_edge(r, c + 1)));

% a middle square lies inside a ship that is either horizontal (left/middle on
% its left, right/middle on its right, water above and below) or vertical
% (top/middle above, bottom/middle below, water to the left and right)
constraint forall(r in Rows, c in Cols)
    (grid[r, c] = MIDDLE ->
        ((piece_at(r, c - 1, {LEFT, MIDDLE}) /\ piece_at(r, c + 1, {RIGHT, MIDDLE}) /\
          water_or_edge(r - 1, c) /\ water_or_edge(r + 1, c))
         \/
         (piece_at(r - 1, c, {TOP, MIDDLE}) /\ piece_at(r + 1, c, {BOTTOM, MIDDLE}) /\
          water_or_edge(r, c - 1) /\ water_or_edge(r, c + 1))));

% the fleet has the listed number of submarines (ships of size 1)
constraint sum(r in Rows, c in Cols) (bool2int(grid[r, c] = CIRCLE)) =
           sum(k in index_set_1of2(fleet_counts) where fleet_counts[k, 1] = 1) (fleet_counts[k, 2]);

% For every longer ship size, the number of ships of that size is the listed
% count. A ship of size s is a left end, s - 2 middle squares and a right end
% in a row, or a top end, s - 2 middle squares and a bottom end in a column.
% The piece rules above make every run of ship pieces one such ship.
constraint forall(k in index_set_1of2(fleet_counts) where fleet_counts[k, 1] >= 2) (
    let { int: s = fleet_counts[k, 1] } in
    sum(r in Rows, c in 0..cols - s)
        (bool2int(grid[r, c] = LEFT /\ grid[r, c + s - 1] = RIGHT /\ forall(j in 1..s - 2) (grid[r, c + j] = MIDDLE)))
    + sum(r in 0..rows - s, c in Cols)
        (bool2int(grid[r, c] = TOP /\ grid[r + s - 1, c] = BOTTOM /\ forall(j in 1..s - 2) (grid[r + j, c] = MIDDLE)))
    = fleet_counts[k, 2]);

% no ship of a size the fleet does not list: every left or top end starts one
% of the ships counted above
constraint sum(r in Rows, c in Cols) (bool2int(grid[r, c] = LEFT \/ grid[r, c] = TOP)) =
           sum(k in index_set_1of2(fleet_counts) where fleet_counts[k, 1] > 1) (fleet_counts[k, 2]);

solve satisfy;

output ["{\"grid\": [",
        join(", ", ["[" ++ join(", ", [show(grid[r, c]) | c in Cols]) ++ "]" | r in Rows]),
        "]}"];
