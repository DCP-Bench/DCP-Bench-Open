% Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across
% a river in a boat that carries the farmer and at most one item. The wolf must
% never be left alone with the goat, nor the goat with the cabbage. The answer
% lists, for each stage, which shore (false = start, true = destination) each
% item and the boat are on.
include "globals.mzn";

int: stage;  % number of stages, including the first and the last

array[1..stage] of var bool: wolf_pos;
array[1..stage] of var bool: goat_pos;
array[1..stage] of var bool: cabbage_pos;
array[1..stage] of var bool: boat_pos;

% everything starts on the first shore ...
constraint not wolf_pos[1] /\ not goat_pos[1] /\ not cabbage_pos[1] /\ not boat_pos[1];
% ... and ends on the far shore
constraint wolf_pos[stage] /\ goat_pos[stage] /\ cabbage_pos[stage] /\ boat_pos[stage];

% the boat crosses the river at every stage
constraint forall(i in 2..stage) (boat_pos[i] != boat_pos[i - 1]);

% the wolf and the goat are never alone together: if they share a shore the boat is there too
constraint forall(i in 1..stage) (goat_pos[i] != wolf_pos[i] \/ boat_pos[i] = wolf_pos[i]);
% the goat and the cabbage are never alone together
constraint forall(i in 1..stage) (goat_pos[i] != cabbage_pos[i] \/ boat_pos[i] = goat_pos[i]);

% at most one of the wolf, goat and cabbage changes shore between two stages
constraint forall(i in 1..stage - 1) (
    bool2int(wolf_pos[i] != wolf_pos[i + 1]) + bool2int(goat_pos[i] != goat_pos[i + 1])
    + bool2int(cabbage_pos[i] != cabbage_pos[i + 1]) <= 1);

solve satisfy;

output ["{\"wolf_pos\": [", join(", ", [show(wolf_pos[i]) | i in 1..stage]),
        "], \"goat_pos\": [", join(", ", [show(goat_pos[i]) | i in 1..stage]),
        "], \"cabbage_pos\": [", join(", ", [show(cabbage_pos[i]) | i in 1..stage]),
        "], \"boat_pos\": [", join(", ", [show(boat_pos[i]) | i in 1..stage]), "]}"];
