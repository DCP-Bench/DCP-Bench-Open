% Include the globals library for global constraints if needed
include "globals.mzn";

% Input data
int: num_lathes = 4;
int: hours_per_lathe = 40;
int: total_lathe_hours = num_lathes * hours_per_lathe; % 160 hours

int: boxwood_available = 200; % kg

int: lathe_hours_small = 3;
int: lathe_hours_large = 2;

int: boxwood_small = 1;
int: boxwood_large = 3;

int: profit_small = 5;
int: profit_large = 20;

% Decision variables: number of small and large sets produced (non-negative integers)
var 0..1000: small_set;
var 0..1000: large_set;

% Constraints
constraint lathe_hours_small * small_set + lathe_hours_large * large_set <= total_lathe_hours;
constraint boxwood_small * small_set + boxwood_large * large_set <= boxwood_available;

% Objective: maximize total profit
var int: max_profit = profit_small * small_set + profit_large * large_set;

solve maximize max_profit;

output [
    "{",
    "\"small_set\": ", show(small_set), ",",
    "\"large_set\": ", show(large_set), ",",
    "\"max_profit\": ", show(max_profit),
    "}"
];