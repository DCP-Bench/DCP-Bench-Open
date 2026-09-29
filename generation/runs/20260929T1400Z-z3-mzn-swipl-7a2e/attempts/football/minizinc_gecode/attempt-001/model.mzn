% Football squad: buy players for as close to GBP 30 million as possible without
% going over, taking the required number from each position and at least eleven
% players in total. The output is the total price in GBP thousands.
include "globals.mzn";

% The players on offer are fixed by the problem, so their prices (in GBP
% thousands) are mirrored here: goalkeepers 1-3, defenders 4-11, midfielders
% 12-21 and strikers 22-26.
int: budget = 30000;
array[1..26] of int: price = [
    730, 1280, 3880,
    920, 1310, 1620, 2410, 2790, 3280, 3910, 4570,
    1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130,
    4460, 6470, 7780, 8390, 9500];
array[1..4] of set of int: position = [1..3, 4..11, 12..21, 22..26];
% the fewest and most players to buy at each position: exactly 1 goalkeeper,
% then 2 or more defenders, 3 or more midfielders and 2 or more strikers
array[1..4] of int: fewest = [1, 2, 3, 2];
array[1..4] of int: most = [1, 8, 10, 5];
int: min_players = 11;  % at least this many players in all

% buy[p] is true when player p is bought
array[1..26] of var bool: buy;

constraint forall(k in 1..4) (
    sum(p in position[k]) (bool2int(buy[p])) >= fewest[k] /\
    sum(p in position[k]) (bool2int(buy[p])) <= most[k]);
constraint sum(p in 1..26) (bool2int(buy[p])) >= min_players;

% z = total price paid, and it stays within the budget
var 0..budget: z = sum(p in 1..26) (price[p] * bool2int(buy[p]));

% spend as much as possible
var int: objective = z;
solve maximize objective;

output ["{\"z\": ", show(z), "}"];
