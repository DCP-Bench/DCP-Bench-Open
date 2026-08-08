include "globals.mzn";

% Data: coin values and available quantities
array[1..6] of int: coin_values = [1, 2, 5, 10, 25, 50];
array[1..6] of int: coin_available = [20, 10, 15, 8, 4, 2];
int: total_change = 199;

% Decision variables: number of coins of each type to give
array[1..6] of var 0..max(coin_available): coin_counts;

% Constraint: cannot use more coins than available
constraint forall(i in 1..6) (
    coin_counts[i] <= coin_available[i]
);

% Constraint: total value must be exactly the change amount
constraint sum(i in 1..6)(coin_counts[i] * coin_values[i]) == total_change;

% Objective: minimize total number of coins used
var int: total_coins = sum(i in 1..6)(coin_counts[i]);
solve minimize total_coins;

output [
    "{",
    "\"coin_counts\": ", show(coin_counts),
    "}"
];