
% Include necessary libraries
include "globals.mzn";

% Decision variables: number of small and large chess sets
var 0..200: small_set;
var 0..200: large_set;

% Profit variable
var int: max_profit;

% Constraints
constraint
    % Lathe hours constraint: 3 hours per small, 2 hours per large, up to 160 hours
    3 * small_set + 2 * large_set <= 160 /\
    % Boxwood constraint: 1 kg per small, 3 kg per large, up to 200 kg
    small_set + 3 * large_set <= 200 /\
    % Define profit: $5 per small, $20 per large
    max_profit = 5 * small_set + 20 * large_set;

% Objective: maximize total profit
solve maximize max_profit;

% Output solution in JSON format
output [
    "{",
    join(",", [
        "\"" ++ "small_set" ++ "\": " ++ show(small_set),
        "\"" ++ "large_set" ++ "\": " ++ show(large_set),
        "\"" ++ "max_profit" ++ "\": " ++ show(max_profit)
    ]),
    "}"
];
