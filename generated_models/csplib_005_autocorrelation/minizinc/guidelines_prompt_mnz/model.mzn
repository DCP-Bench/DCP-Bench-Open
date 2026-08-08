
% Low Autocorrelation Binary Sequence of length n = 10 (non-periodic)
include "globals.mzn";

% Input data
int: n = 10;

% Decision variables: sequence values S[i] in {-1, +1}
array[1..n] of var {-1,1}: S;

% Autocorrelations Ck for k = 1..n-1 (non-periodic)
array[1..n-1] of var int: Ck;
constraint
  forall(k in 1..n-1) (
    Ck[k] = sum(i in 1..n-k)(S[i] * S[i+k])
  );

% Energy E = sum of squares of autocorrelations
var int: E;
constraint
  E = sum(k in 1..n-1)(Ck[k] * Ck[k]);

% Objective: minimize the energy
solve minimize E;

% Print solution in JSON format
output [
  "{",
    join(",", [
      "\"sequence\": [" ++ join(",", [show(S[i]) | i in 1..n]) ++ "]",
      "\"E\": " ++ show(E)
    ]),
  "}"
];
