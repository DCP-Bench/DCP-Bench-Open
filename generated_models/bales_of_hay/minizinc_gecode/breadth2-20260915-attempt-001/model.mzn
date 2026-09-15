include "globals.mzn";

int: n;
array[int] of int: weights;

% The reference's own bound on a single bale.
array[1..n] of var 0..50: bales;

constraint forall(w in index_set(weights)) (
    exists(i, j in 1..n where i < j) (bales[i] + bales[j] = weights[w]));

solve satisfy;

output ["{\"bales\": [", join(", ", [show(bales[i]) | i in 1..n]), "]}"];
