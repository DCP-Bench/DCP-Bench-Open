
% A side show at Coney Island problem: choose dummies summing to exactly 50

% Input data: numbers on the ten dummies
array[1..10] of int: weights = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27];

% Decision variables: whether each dummy is knocked over
array[1..10] of var bool: dummies;

% Constraint: the sum of chosen dummy weights must be exactly 50
constraint
  sum(i in 1..10)( if dummies[i] then weights[i] else 0 endif ) = 50;

% Find any solution
solve satisfy;

% Output the boolean selection as a JSON list under the key "dummies"
output [
  "{",
    "\"dummies\": [",
    join(",", [ if dummies[i] then "true" else "false" endif | i in 1..10 ]),
    "]",
  "}"
];
