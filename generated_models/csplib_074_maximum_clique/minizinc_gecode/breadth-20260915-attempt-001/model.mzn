include "globals.mzn";

int: n;
array[int, int] of int: adj;

array[1..n] of var bool: c;

constraint forall(i, j in 1..n where i < j /\ adj[i, j] = 0) (
    bool2int(c[i]) + bool2int(c[j]) <= 1);

var int: objective = sum(i in 1..n) (bool2int(c[i]));
solve maximize objective;

output ["{\"c\": [", join(", ", [show(c[i]) | i in 1..n]), "]}"];
