include "globals.mzn";

int: num_gates;

array[0..num_gates] of var 0..100: apples;

constraint apples[num_gates] = 1;
constraint forall(i in 1..num_gates) (apples[i - 1] = 2 * (apples[i] + 1));

solve satisfy;

output ["{\"apples\": [", join(", ", [show(apples[i]) | i in 0..num_gates]), "]}"];
