include "globals.mzn";

% The possible bag sizes
set of int: BagTypes = 1..6;
array[BagTypes] of int: bag_sizes = [16, 17, 23, 24, 39, 40];

% Decision variables: number of bags stolen for each bag size
array[BagTypes] of var 0..100: bags;

% Constraint: total coins stolen is 100
constraint sum(i in BagTypes)(bags[i] * bag_sizes[i]) = 100;

solve satisfy;

output [
    "{",
    join(",", [
        "\"bags\" : " ++ show(bags)
    ]),
    "}"
];