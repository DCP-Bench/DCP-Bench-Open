% Flow Free: colour every cell of the board so that each colour forms one pipe
% joining its two given end cells, the pipes do not cross or overlap, and the
% whole board is covered. A pipe is a chain of orthogonally adjacent cells of
% one colour.
include "globals.mzn";

array[int, int] of int: board;  % colour of each end cell, 0 for a cell to fill

set of int: Rows = index_set_1of2(board);
set of int: Columns = index_set_2of2(board);
int: n_colors = max(board);  % colours are numbered 1..n_colors

% B[i, j] = colour of cell (i, j)
array[Rows, Columns] of var 1..n_colors: B;

constraint forall(i in Rows, j in Columns) (
    let { var int: same_neighbours = sum(a in Rows, b in Columns where abs(a - i) + abs(b - j) = 1)
                                         (bool2int(B[a, b] = B[i, j])) } in
    if board[i, j] != 0 then
        % an end cell has its given colour and joins exactly one neighbour of that colour
        B[i, j] = board[i, j] /\ same_neighbours = 1
    else
        % a cell in the middle of a pipe joins exactly two neighbours of its colour
        same_neighbours = 2
    endif);

solve satisfy;

output ["{\"B\": [",
        join(", ", ["[" ++ join(", ", [show(B[i, j]) | j in Columns]) ++ "]" | i in Rows]),
        "]}"];
