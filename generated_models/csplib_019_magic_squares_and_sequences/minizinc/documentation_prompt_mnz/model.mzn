include "globals.mzn";

% Input data
int: n = 12;

% Decision Variables
array[0..n-1] of var 0..n-1: x;

% Constraints
% For each i, the number i occurs exactly x[i] times in the sequence x
constraint
  forall(i in 0..n-1) (
    count(x, i) == x[i]
  );

solve satisfy;

output [
  "{",
  "\"" ++ "x" ++ "\": " ++ show(x),
  "}"
];