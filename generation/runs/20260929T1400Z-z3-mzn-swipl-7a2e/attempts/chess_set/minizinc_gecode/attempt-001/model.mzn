% Chess set: a joinery makes small and large boxwood chess sets. Decide how
% many of each to make in a week so that the lathe hours and the boxwood are not
% exceeded and the profit is as large as possible.
include "globals.mzn";

% The problem statement fixes all the numbers; the instance carries no data.

% number of small and large sets made per week (at most 100 of each is ever useful)
var 0..100: small_set;
var 0..100: large_set;
var 0..10000: max_profit;

% boxwood: a small set needs 1 kg, a large one 3 kg, and only 200 kg is available
constraint small_set + 3 * large_set <= 200;
% lathe hours: 3 hours per small set, 2 per large set, 4 lathes x 40 hours = 160 hours
constraint 3 * small_set + 2 * large_set <= 160;
% profit: $5 per small set and $20 per large set
constraint max_profit = 5 * small_set + 20 * large_set;

% make as much profit as possible
var int: objective = max_profit;
solve maximize objective;

output ["{\"small_set\": ", show(small_set), ", \"large_set\": ", show(large_set),
        ", \"max_profit\": ", show(max_profit), "}"];
