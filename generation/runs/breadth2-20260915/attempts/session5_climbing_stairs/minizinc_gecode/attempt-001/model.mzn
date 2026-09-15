include "globals.mzn";

int: n;
int: m1;
int: m2;

array[1..n] of var 0..m2: steps;

constraint sum(i in 1..n) (steps[i]) = n;
constraint forall(i in 1..n) (steps[i] >= m1 \/ steps[i] = 0);
% Once a move is empty, every later one is too.
constraint forall(i in 2..n) (steps[i - 1] = 0 -> forall(j in i..n) (steps[j] = 0));

solve satisfy;

output ["{\"steps\": [", join(", ", [show(steps[i]) | i in 1..n]), "]}"];
