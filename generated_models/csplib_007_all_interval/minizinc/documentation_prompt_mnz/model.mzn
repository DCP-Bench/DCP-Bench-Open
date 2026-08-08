include "globals.mzn";

% Input data
int: n = 12;

% Decision variables
% x: the sequence of pitch-classes, a permutation of 0..n-1
array[1..n] of var 0..n-1: x;

% diffs: the intervals between neighboring pitch-classes, a permutation of 1..n-1
array[1..n-1] of var 1..n-1: diffs;

% Constraints
constraint
    % x is a permutation of 0..n-1
    alldifferent(x);

constraint
    % diffs is a permutation of 1..n-1
    alldifferent(diffs);

constraint
    % diffs[i] = absolute difference between x[i+1] and x[i]
    forall(i in 1..n-1) (
        diffs[i] = abs(x[i+1] - x[i])
    );

solve satisfy;

output [
    "{",
    "\"x\": ", show(x), ",",
    "\"diffs\": ", show(diffs),
    "}"
];