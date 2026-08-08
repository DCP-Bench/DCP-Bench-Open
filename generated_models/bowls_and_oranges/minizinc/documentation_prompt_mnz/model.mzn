include "globals.mzn";

int: num_bowls = 40;
int: num_oranges = 9;

% Decision variables: positions of the oranges in the bowls
array[1..num_oranges] of var 1..num_bowls: x;

% Constraint: all oranges are placed in distinct bowls
constraint all_different(x);

% Constraint: no three oranges A, B, C such that distance(A,B) = distance(B,C)
% This means no arithmetic progression of length 3 in the positions
% For all triples i < j < k, ensure that x[j] - x[i] != x[k] - x[j]
constraint
  forall(i, j, k in 1..num_oranges where i < j /\ j < k) (
    (x[j] - x[i]) != (x[k] - x[j])
  );

solve satisfy;

output [
  "{",
  "\"x\": ", show(x),
  "}"
];