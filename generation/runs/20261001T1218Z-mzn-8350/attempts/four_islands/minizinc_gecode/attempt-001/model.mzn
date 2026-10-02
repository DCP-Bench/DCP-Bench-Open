% Four islands: four islands joined by bridges, laid out as
%     A -- B
%     |    |
%     C -- D
% (A is north of C, C is west of D, ...). Each island (Pwana, Quero, Rayou, Skern)
% has a different primary export (alabaster, bananas, coconuts, durian fruit) and a
% different tourist attraction (resort hotel, ice skating rink, jai alai stadium,
% koala preserve). Work out which island is where, from six clues. This problem has
% no instance data: the map and the clues are part of the problem statement.
include "globals.mzn";

% map positions of the islands
int: A = 0; int: B = 1; int: C = 2; int: D = 3;

% island[i] = map position of Pwana, Quero, Rayou, Skern (in this order)
array[1..4] of var 0..3: island;
var 0..3: Pwana = island[1]; var 0..3: Quero = island[2];
var 0..3: Rayou = island[3]; var 0..3: Skern = island[4];

% export[i] = map position of the island exporting alabaster, bananas, coconuts, durian fruit
array[1..4] of var 0..3: export;
var 0..3: alabaster = export[1]; var 0..3: bananas = export[2];
var 0..3: coconuts = export[3]; var 0..3: durian_fruit = export[4];

% attraction[i] = map position of the island with the resort hotel, ice skating rink,
% jai alai stadium, koala preserve
array[1..4] of var 0..3: attraction;
var 0..3: resort_hotel = attraction[1]; var 0..3: ice_skating_rink = attraction[2];
var 0..3: jai_alai_stadium = attraction[3]; var 0..3: koala_preserve = attraction[4];

% each name, export and attraction is on a different island
constraint all_different(island);
constraint all_different(export);
constraint all_different(attraction);

% 1. The island noted for its koala preserve is due south of Pwana.
constraint (Pwana = A /\ koala_preserve = C) \/ (Pwana = B /\ koala_preserve = D);

% 2. The island with the largest alabaster quarry is due west of Quero.
constraint (alabaster = A /\ Quero = B) \/ (alabaster = C /\ Quero = D);

% 3. The island with the resort hotel is due east of the one that exports durian fruit.
constraint (durian_fruit = A /\ resort_hotel = B) \/ (durian_fruit = C /\ resort_hotel = D);

% 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
constraint (Skern = A /\ jai_alai_stadium = C) \/ (Skern = C /\ jai_alai_stadium = A) \/
           (Skern = B /\ jai_alai_stadium = D) \/ (Skern = D /\ jai_alai_stadium = B);

% 5. Rayou and the island that exports bananas are connected by an east-west bridge.
constraint (Rayou = A /\ bananas = B) \/ (Rayou = B /\ bananas = A) \/
           (Rayou = C /\ bananas = D) \/ (Rayou = D /\ bananas = C);

% 6. The islands noted for the largest ice skating rink and for the jai alai stadium
% are not connected by a bridge (they are diagonal from each other).
constraint (ice_skating_rink = A /\ jai_alai_stadium = D) \/ (ice_skating_rink = D /\ jai_alai_stadium = A) \/
           (ice_skating_rink = B /\ jai_alai_stadium = C) \/ (ice_skating_rink = C /\ jai_alai_stadium = B);

solve satisfy;

output ["{\"island\": [", join(", ", [show(island[i]) | i in 1..4]),
        "], \"export\": [", join(", ", [show(export[i]) | i in 1..4]),
        "], \"attraction\": [", join(", ", [show(attraction[i]) | i in 1..4]), "]}"];
