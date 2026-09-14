include "globals.mzn";

int: n;

array[1..n] of var 1..n: costas;

constraint all_different(costas);
% Row l of the difference triangle holds costas[j] - costas[j - l].
constraint forall(l in 1..n-2) (
    all_different([costas[j] - costas[j - l] | j in l+1..n])
);

solve satisfy;

output ["{\"costas\": [", join(", ", [show(costas[i]) | i in 1..n]), "]}"];
