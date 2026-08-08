include "globals.mzn";

% Input data
int: n = 5;
array[1..n] of int: values = [4, 2, 3, 7, 1];
array[1..n] of int: weights = [3, 1, 2, 5, 4];
int: capacity = 7;

% Decision variables: x[i] = 1 if item i is taken, 0 otherwise
array[1..n] of var 0..1: x;

% Constraint: total weight must not exceed capacity
constraint sum(i in 1..n)(weights[i] * x[i]) <= capacity;

% Objective: maximize total value
var int: total_value = sum(i in 1..n)(values[i] * x[i]);
solve maximize total_value;

output [
    "{",
    "\"x\": ", show(x),
    "}"
];