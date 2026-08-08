include "globals.mzn";

% Input data
int: target = 20;

% Decision variables: number of 7-packs and 13-packs
var 0..target div 7 + 10: count_7;
var 0..target div 13 + 10: count_13;

% Total beers from the packs
var int: total_beers = 7 * count_7 + 13 * count_13;

% Constraint: total beers must be at least the target
constraint total_beers >= target;

% Objective: minimize the excess beers above the target
var int: excess = total_beers - target;
solve minimize excess;

output [
    "{",
    "\"counts\": [", show(count_7), ", ", show(count_13), "]",
    "}"
];