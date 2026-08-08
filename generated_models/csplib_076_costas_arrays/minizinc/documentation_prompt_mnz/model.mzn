include "globals.mzn";

% Input data
int: n = 8;

% Decision Variables
% X is a permutation of 1..n representing the column positions of marks in each row
array[1..n] of var 1..n: costas;

% Difference triangle variables
% For each lag l in 1..n-1, we have n-l differences
array[1..n-1, 1..n-1] of var int: diff;

% Constraints

% 1) costas is a permutation (one mark per row and column)
constraint alldifferent(costas);

% 2) Define the difference triangle
% diff[l,i] = costas[i] - costas[i+l] for i in 1..n-l
constraint
  forall(l in 1..n-1, i in 1..n - l) (
    diff[l,i] = costas[i] - costas[i + l]
  );

% 3) Each line of the difference triangle must be all different
constraint
  forall(l in 1..n-1) (
    alldifferent([diff[l,i] | i in 1..n - l])
  );

solve satisfy;

output [
  "{",
  "\"costas\": ", show(costas),
  "}"
];