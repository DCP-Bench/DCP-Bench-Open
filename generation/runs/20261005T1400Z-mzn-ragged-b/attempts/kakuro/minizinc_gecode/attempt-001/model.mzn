% Kakuro: fill the white cells of an n x n grid with digits 1..9 so that every
% entry sums to its clue with no repeated digit; blank cells hold 0.
% This model only declares the fields; `problem` rows ([clue, cell, cell, ...])
% are ragged rows of mixed type, which the integration's binding rules refuse.
include "globals.mzn";

int: n;
int: num_blanks;
array[int,int] of int: blanks;           % blank cells, 1 = row / 2 = column
array[int] of int: problem;              % not bindable; declared so the binding is attempted

array[1..n, 1..n] of var 0..9: x;

% the blanks are filled with 0
constraint forall(b in index_set_1of2(blanks))(x[blanks[b, 1], blanks[b, 2]] = 0);

solve satisfy;

output ["{\"x\": [", join(", ", ["[" ++ join(", ", [show(x[i, j]) | j in 1..n]) ++ "]" | i in 1..n]), "]}"];
