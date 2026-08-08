
include "globals.mzn";

% Input data
int: n = 9;
array[1..n] of int: nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1];

% Decision variables: whether each element is selected
array[1..n] of var bool: indices;

% Exactly three elements must be selected
constraint sum(i in 1..n)(bool2int(indices[i])) = 3;

% The sum of selected elements must be zero
constraint sum(i in 1..n)(nums[i] * bool2int(indices[i])) = 0;

solve satisfy;

% JSON output of the boolean selection array
output [
  "{",
  "\"indices\": [" ++ join(",", [show(indices[i]) | i in 1..n]) ++ "]",
  "}"
];
