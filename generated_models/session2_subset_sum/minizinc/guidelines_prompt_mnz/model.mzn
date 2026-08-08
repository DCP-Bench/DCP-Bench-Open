
% Include global constraints library
include "globals.mzn";

% Number of different bag types
int: num_types = 6;

% Sizes of each bag type
array[1..num_types] of int: sizes = [16, 17, 23, 24, 39, 40];

% Decision variables: number of bags stolen of each type
% Maximum possible stolen for smallest bag is 100 div 16 = 6
array[1..num_types] of var 0..6: bags;

% Constraint: total stolen coins must sum to 100
constraint
    sum(i in 1..num_types)(bags[i] * sizes[i]) == 100;

% Solve the satisfaction problem
solve satisfy;

% Output the solution in JSON format with key "bags"
output [
  "{",
    "\"bags\": [" ++ join(",", [show(bags[i]) | i in 1..num_types]) ++ "]",
  "}"
];
