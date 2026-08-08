include "globals.mzn";

% Input data
int: n = 5;  % Length of x
int: m = 3;  % Number of values required in x from v
array[1..m] of int: v = [1, 5, 8];  % Values to be among in x

% Decision variable: array x of length n with domain including values in v and possibly others
% To keep it simple, we allow x to take values from 1 to max(v) (or larger if needed)
% Here we choose domain from 1 to max(v) to cover all values in v
var 1..max(v): x[1..n];

% Constraint: Exactly m variables in x take one of the values in v
constraint
    % Count how many variables in x take a value in v
    sum([bool2int(x[i] in v) | i in 1..n]) == m;

solve satisfy;

output [
    "{",
    "\"x\": ", show(x),
    "}"
];