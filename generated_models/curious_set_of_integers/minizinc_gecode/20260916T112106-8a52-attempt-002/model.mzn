% Curious set of integers: extend {1, 3, 8, 120}, where the product of any two
% members is one less than a perfect square.
%
% The reference states the property for every ordered pair i != j. It is
% symmetric in i and j, so only the pairs with i < j are posted here; the
% mirrored half is the same constraint and doubles the propagation work that
% made a first attempt exceed the budget.
include "globals.mzn";

int: n;
int: max_val;

array[1..n] of var 0..max_val: x;

constraint all_different(x);
% The four known members of the set are part of the problem statement.
constraint x[1] = 1;
constraint x[2] = 3;
constraint x[3] = 8;
constraint x[4] = 120;

constraint forall(i, j in 1..n where i < j) (
    let { var 0..max_val: root } in root * root = x[i] * x[j] + 1
);

solve satisfy;

output ["{\"number\": ", show(x[n]), "}"];
