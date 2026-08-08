include "globals.mzn";

% The numbers on the ten dummies
array[1..10] of int: dummy_values = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27];

% Decision variables: whether each dummy is knocked over (1) or not (0)
array[1..10] of var 0..1: dummies;

% Constraint: sum of knocked over dummies' values must be exactly 50
constraint sum(i in 1..10)(dummies[i] * dummy_values[i]) = 50;

solve satisfy;

output [
    "{",
    "\"dummies\": ", show(dummies),
    "}"
];