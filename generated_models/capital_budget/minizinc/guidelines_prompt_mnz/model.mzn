
% Include standard library for globals
include "globals.mzn";

% Input data
int: n = 4;                              % number of investments
array[1..n] of int: npv  = [16000, 22000, 12000,  8000];  % net present values
array[1..n] of int: cost = [ 5000,  7000,  4000,  3000];  % cash outflows
int: budget = 14000;                    % available funds

% Decision variables: whether to choose each investment (0 = no, 1 = yes)
array[1..n] of var 0..1: x;

% Constraint: total cost must not exceed budget
constraint
    sum(i in 1..n)(cost[i] * x[i]) <= budget;

% Objective: maximize total NPV
solve maximize sum(i in 1..n)(npv[i] * x[i]);

% Output chosen investments as JSON list of 0/1 values
output [
    "{" ++
    "\"x\": [" ++ join(",", [show(x[i]) | i in 1..n]) ++ "]" ++
    "}"
];
