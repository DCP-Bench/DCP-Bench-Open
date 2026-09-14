include "globals.mzn";

int: n;

array[1..n] of var 1..n: queens;

constraint all_different(queens);
constraint all_different([queens[i] - i | i in 1..n]);
constraint all_different([queens[i] + i | i in 1..n]);

solve satisfy;

output ["{\"queens\": [", join(", ", [show(queens[i]) | i in 1..n]), "]}"];
