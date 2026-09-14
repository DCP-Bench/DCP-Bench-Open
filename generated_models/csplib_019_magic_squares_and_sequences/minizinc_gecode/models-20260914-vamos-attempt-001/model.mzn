include "globals.mzn";

int: n;

array[0..n-1] of var 0..n-1: x;

constraint forall(i in 0..n-1) (
    x[i] = sum(j in 0..n-1) (bool2int(x[j] = i))
);

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 0..n-1]), "]}"];
