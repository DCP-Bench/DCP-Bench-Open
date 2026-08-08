
include "globals.mzn";

% Input data
int: n = 27;
int: m = 5;

% Decision variables: the series S = s[0..n+1]
% Domain: each element can range from 0 up to the length of the series (n+2)
array[0..n+1] of var 0..n+2: s;

% Constraint: the last element s[n+1] equals m
constraint s[n+1] = m;

% Self-descriptive constraint:
% For each i in 0..n, the number of occurrences of i in the series equals s[i]
constraint
  forall(i in 0..n) (
    count([ s[j] | j in 0..n+1 ], i) = s[i]
  );

solve satisfy;

% Output the solution in JSON format with key "s"
output [
  "{",
    "\"s\":[" ++ join(",", [ show(s[i]) | i in 0..n+1 ]) ++ "]",
  "}"
];
