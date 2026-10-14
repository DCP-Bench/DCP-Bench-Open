% Minesweeper: from the revealed numbers of a board, decide which of the
% unopened cells hold a mine. An opened cell is safe and shows how many of its
% (up to eight) neighbours are mines.
include "globals.mzn";

int: X;  % the value that marks a cell that is not opened
array[int, int] of int: game_data;

set of int: Rows = index_set_1of2(game_data);
set of int: Columns = index_set_2of2(game_data);

% mines[r, c] is true when cell (r, c) holds a mine
array[Rows, Columns] of var bool: mines;

% an opened cell is not a mine, and its number is the count of mines among its neighbours
constraint forall(r in Rows, c in Columns where game_data[r, c] != X) (
    not mines[r, c] /\
    sum(a in max(min(Rows), r - 1)..min(max(Rows), r + 1),
        b in max(min(Columns), c - 1)..min(max(Columns), c + 1) where not (a = r /\ b = c))
        (bool2int(mines[a, b])) = game_data[r, c]);

solve satisfy;

output ["{\"mines\": [",
        join(", ", ["[" ++ join(", ", [show(mines[r, c]) | c in Columns]) ++ "]" | r in Rows]),
        "]}"];
