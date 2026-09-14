include "globals.mzn";

int: n;

array[1..n] of var 0..n-1: x;
array[1..n-1] of var 1..n-1: diffs;

constraint all_different(x);
constraint all_different(diffs);
constraint forall(i in 1..n-1) (diffs[i] = abs(x[i+1] - x[i]));

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 1..n]),
        "], \"diffs\": [", join(", ", [show(diffs[i]) | i in 1..n-1]), "]}"];
