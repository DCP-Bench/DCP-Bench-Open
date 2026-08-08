
% Include standard global constraints library
include "globals.mzn";

% Decision Variables
% holes[i] is the length of hole i, can be 3, 4, or 5
array[1..18] of var 3..5: holes;

% Constraint: total length of 18 holes must be exactly 72
constraint sum(holes) = 72;

% Find any feasible assignment
solve satisfy;

% Output the solution in JSON format with key "holes"
output [
    "{",
    join(",", [
        "\"" ++ "holes" ++ "\": [" ++ join(",", [show(holes[i]) | i in 1..18]) ++ "]"
    ]),
    "}"
];
