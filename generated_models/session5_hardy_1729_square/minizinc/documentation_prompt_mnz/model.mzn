include "globals.mzn";

% Define the domain for the numbers
set of int: NUMS = 1..100;

% Decision variables: four different numbers a, b, c, d
array[1..4] of var NUMS: x;

% All numbers must be different
constraint all_different(x);

% Constraint: sum of squares of first two equals sum of squares of last two
constraint x[1]*x[1] + x[2]*x[2] = x[3]*x[3] + x[4]*x[4];

solve satisfy;

output [
    "{",
    join(",", [
        "\"a\": " ++ show(x[1]),
        "\"b\": " ++ show(x[2]),
        "\"c\": " ++ show(x[3]),
        "\"d\": " ++ show(x[4])
    ]),
    "}"
];