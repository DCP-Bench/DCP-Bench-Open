include "globals.mzn";

int: n;
int: m;
array[int] of int: v;

% The reference's own domain for x.
array[1..n] of var 0..7: x;

constraint sum(i in 1..n, k in index_set(v)) (bool2int(x[i] = v[k])) = m;

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 1..n]), "]}"];
