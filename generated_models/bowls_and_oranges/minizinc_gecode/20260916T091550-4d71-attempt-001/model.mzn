% Bowls and oranges: place m oranges in n bowls spaced a metre apart so that no
% three of them are evenly spaced.
include "globals.mzn";

int: n;
int: m;

array[1..m] of var 1..n: x;

constraint all_different(x);
% Positions are reported in ascending order.
constraint forall(i in 2..m) (x[i - 1] <= x[i]);

% No three oranges A, B, C with B as far from A as C is from B.
constraint forall(i, j, k in 1..m where i < j /\ j < k) (
    x[j] - x[i] != x[k] - x[j]
);

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 1..m]), "]}"];
