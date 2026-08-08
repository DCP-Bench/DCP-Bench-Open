
% Include necessary library (globals for sum if needed)
include "globals.mzn";

% Input data
int: n = 6;
array[1..n] of int: demands = [4, 8, 10, 7, 12, 4];

% Number of possible shift start times (each shift covers 2 consecutive slots)
int: m = n - 1;

% Decision Variables
% x[i] = number of buses starting at time slot i (covers slots i and i+1)
array[1..m] of var 0..sum(demands): x;

% Constraints
% 1) First slot covered by shifts starting at 1
constraint x[1] >= demands[1];
% 2) Intermediate slots covered by overlapping shifts
constraint forall(i in 2..n-1) (
    x[i-1] + x[i] >= demands[i]
);
% 3) Last slot covered by shifts starting at m
constraint x[m] >= demands[n];

% Objective: minimize total number of buses scheduled
solve minimize sum(i in 1..m)(x[i]);

% Output the solution in JSON format
output [
    "{",
    "\"x\": [" ++ join(",", [show(x[i]) | i in 1..m]) ++ "]",
    "}"
];
