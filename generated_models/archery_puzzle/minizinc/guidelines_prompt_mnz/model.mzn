
% Include global constraints library (if needed)
include "globals.mzn";

% Number of different targets
int: num_targets = 6;

% The score value for each target
array[1..num_targets] of int: target = [16, 17, 23, 24, 39, 40];

% Decision variables: number of hits on each target (unbounded above, but
% effectively bounded by the total-score constraint)
array[1..num_targets] of var 0..100: hits;

% The total score achieved
var int: score = sum(i in 1..num_targets)(hits[i] * target[i]);

% Constraint: do not exceed 100 points
constraint score <= 100;

% Objective: maximize the total score (as close as possible to 100)
solve maximize score;

% Output the hits array in JSON format
output [
    "{",
    join(",", [
        "\"" ++ "hits" ++ "\": [" ++ join(",", [show(hits[i]) | i in 1..num_targets]) ++ "]"
    ]),
    "}"
];
