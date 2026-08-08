% Include necessary library
include "globals.mzn";

% Input data
array[1..9] of int: nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1];
int: n = length(nums);

% Decision variables: whether each element is selected (0 or 1)
array[1..n] of var 0..1: selected;

% Constraint: exactly three elements are selected
constraint sum(selected) = 3;

% Constraint: sum of selected elements is zero
constraint sum([selected[i] * nums[i] | i in 1..n]) = 0;

solve satisfy;

output [
    "{",
    join(",", [ "\"" ++ "selected[" ++ show(i) ++ "]" ++ "\": " ++ show(selected[i]) | i in 1..n ]),
    "}"
];