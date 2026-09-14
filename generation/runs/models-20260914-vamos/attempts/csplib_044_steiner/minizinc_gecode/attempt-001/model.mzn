include "globals.mzn";

int: n;
int: n_sets = n * (n - 1) div 6;

array[1..n_sets, 1..n] of var bool: sets;

% Every triple holds three elements.
constraint forall(i in 1..n_sets) (
    sum(j in 1..n) (bool2int(sets[i, j])) = 3
);
% Two triples share at most one element.
constraint forall(i1, i2 in 1..n_sets where i1 < i2) (
    sum(j in 1..n) (bool2int(sets[i1, j] /\ sets[i2, j])) <= 1
);

solve satisfy;

output ["{\"sets\": [",
        join(", ", ["[" ++ join(", ", [show(sets[i, j]) | j in 1..n]) ++ "]" | i in 1..n_sets]),
        "]}"];
