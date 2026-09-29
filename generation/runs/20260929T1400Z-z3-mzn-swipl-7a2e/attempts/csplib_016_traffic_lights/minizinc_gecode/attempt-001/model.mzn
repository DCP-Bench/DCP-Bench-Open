% Traffic lights: a four-way junction has four vehicle lights V1..V4 and four
% pedestrian lights P1..P4. Pick a state for each so that every pair of
% neighbouring roads shows one of the safe combinations.
include "globals.mzn";

% safe combinations of (V_i, P_i, V_{i+1}, P_{i+1}); everything else is forbidden
array[int, 1..4] of int: allowed_tuples;

% vehicle lights: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow
array[1..4] of var 0..3: vehicle;
% pedestrian lights: 0 = red, 1 = green
array[1..4] of var 0..1: pedestrian;

% each road and the next one (road 4 is followed by road 1) must show a safe combination
constraint forall(i in 1..4) (
    table([vehicle[i], pedestrian[i], vehicle[i mod 4 + 1], pedestrian[i mod 4 + 1]], allowed_tuples));

% reported in the order V1, V2, V3, V4, P1, P2, P3, P4
solve satisfy;

output ["{\"lights\": [", join(", ", [show(vehicle[i]) | i in 1..4] ++ [show(pedestrian[i]) | i in 1..4]), "]}"];
