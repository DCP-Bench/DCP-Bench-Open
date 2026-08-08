
include "globals.mzn";

% Input data
int: n = 4;
array[1..n, 1..n] of int: m = [
    | 1, 1, 1, 1
    | 0, 1, 1, 0
    | 1, 0, 0, 1
    | 1, 0, 0, 1
];

% Decision Variables: x[i,j] = 1 if person i is assigned to slot j
array[1..n, 1..n] of var 0..1: x;

% Constraints
% Each person is assigned to exactly one slot
constraint forall(i in 1..n) (
    sum(j in 1..n)(x[i,j]) = 1
);
% Each slot has exactly one person
constraint forall(j in 1..n) (
    sum(i in 1..n)(x[i,j]) = 1
);
% Only assign if the person is free in that slot
constraint forall(i,j in 1..n) (
    x[i,j] <= m[i,j]
);

solve satisfy;

% Output in JSON format
output [
    "{",
    "\"x\": [",
    join(
      ",",
      [ "[" ++ join(",", [ show(x[i,j]) | j in 1..n ]) ++ "]"
        | i in 1..n ]
    ),
    "]",
    "}"
];
