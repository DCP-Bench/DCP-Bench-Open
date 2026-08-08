include "globals.mzn";

% Input data
int: n = 4; % number of people and slots
array[1..n, 1..n] of int: m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
];

% Decision variables
% x[p,s] = 1 if person p is assigned to slot s, 0 otherwise
array[1..n, 1..n] of var 0..1: x;

% Constraints

% Each person is assigned to exactly one slot
constraint forall(p in 1..n) (
    sum(s in 1..n)(x[p,s]) == 1
);

% Each slot is assigned to exactly one person
constraint forall(s in 1..n) (
    sum(p in 1..n)(x[p,s]) == 1
);

% Assignments only allowed if person is free at that slot
constraint forall(p in 1..n, s in 1..n) (
    x[p,s] <= m[p,s]
);

solve satisfy;

output [
    "{",
    "\"x\": [",
    concat([
        "[" ++ join(", ", [show(x[p,s]) | s in 1..n]) ++ "]" ++ if p < n then "," else "" endif
        | p in 1..n
    ]),
    "]",
    "}"
];