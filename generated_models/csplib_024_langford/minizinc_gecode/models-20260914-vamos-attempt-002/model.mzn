include "globals.mzn";

int: k;

% position[i] and position[k + i] hold the two places (0-based) of value i.
array[1..2*k] of var 0..2*k-1: position;
array[1..2*k] of var 1..k: sol;

constraint all_different(position);
constraint forall(i in 1..k) (
    position[i + k] = position[i] + i + 1
  /\ sol[position[i] + 1] = i
  /\ sol[position[i + k] + 1] = i
);

% Implied: the first copy of value i leaves room for the second one.
constraint forall(i in 1..k) (position[i] <= 2*k - i - 2);
% Implied: every value occupies exactly two places.
constraint global_cardinality(sol, [i | i in 1..k], [2 | i in 1..k]);

solve satisfy;

output ["{\"sol\": [", join(", ", [show(sol[j]) | j in 1..2*k]), "]}"];
