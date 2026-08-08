include "globals.mzn";

% Targets and their scores
array[1..6] of int: targets = [16, 17, 23, 24, 39, 40];

% Decision variables: number of hits on each target (non-negative integers)
array[1..6] of var 0..100: hits;

% Total score from all hits
var 0..1000: total_score = sum(i in 1..6)(hits[i] * targets[i]);

% Objective: minimize the absolute difference to 100
var 0..1000: diff = abs(total_score - 100);

solve minimize diff;

output [
    "{",
    "\"hits\": ", show(hits),
    "}"
];