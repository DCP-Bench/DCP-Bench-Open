
% Include necessary library
include "globals.mzn";

% Input data
int: target = 199;
set of int: TYPES = 1..6;
array[TYPES] of int: value = [1, 2, 5, 10, 25, 50];
array[TYPES] of int: avail = [20, 10, 15, 8, 4, 2];

% Decision variables: number of coins of each type to use
array[TYPES] of var 0..avail[i]: coin_counts;

% Constraint: total sum of used coins equals the target amount
constraint
    sum(i in TYPES)(coin_counts[i] * value[i]) = target;

% Objective: minimize the total number of coins used
var int: total_coins = sum(i in TYPES)(coin_counts[i]);
solve minimize total_coins;

% Output in JSON format
output [
    "{",
    "\"coin_counts\": [" ++ join(",", [ show(coin_counts[i]) | i in TYPES ]) ++ "]",
    "}"
];
