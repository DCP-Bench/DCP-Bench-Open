% Curious set of integers: extend {1, 3, 8, 120}, where the product of any two
% members is one less than a perfect square.
include "globals.mzn";

int: n;
int: max_val;

array[1..n] of var 0..max_val: x;
% One root per ordered pair, as the reference declares.
array[1..n, 1..n] of var 0..max_val: root;

constraint all_different(x);
% The four known members of the set are part of the problem statement.
constraint x[1] = 1;
constraint x[2] = 3;
constraint x[3] = 8;
constraint x[4] = 120;

constraint forall(i, j in 1..n where i != j) (
    root[i, j] * root[i, j] = x[i] * x[j] + 1
);

solve satisfy;

output ["{\"number\": ", show(x[n]), "}"];
