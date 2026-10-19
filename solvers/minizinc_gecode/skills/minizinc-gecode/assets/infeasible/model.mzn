% Pigeonhole: 4 pigeons, 3 holes, no hole may hold two pigeons.
% There is no such assignment, so the solver reports UNSATISFIABLE.
include "globals.mzn";

int: pigeons = 4;
int: holes = 3;
array[1..pigeons] of var 1..holes: hole_of;

constraint all_different(hole_of);

solve satisfy;

output ["hole_of = ", show(hole_of), "\n"];
