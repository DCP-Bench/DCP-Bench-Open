
include "globals.mzn";

% Number of stages
int: num_stages = 8;

% Positions: 0 = starting shore, 1 = destination shore
array[1..num_stages] of var 0..1: wolf_pos;
array[1..num_stages] of var 0..1: goat_pos;
array[1..num_stages] of var 0..1: cabbage_pos;
array[1..num_stages] of var 0..1: boat_pos;

% Transport decisions: 1 if the farmer takes that item in the crossing
array[1..num_stages-1] of var 0..1: take_wolf;
array[1..num_stages-1] of var 0..1: take_goat;
array[1..num_stages-1] of var 0..1: take_cabbage;

% Initial state: all on starting shore
constraint wolf_pos[1] = 0 /\ goat_pos[1] = 0 /\ cabbage_pos[1] = 0 /\ boat_pos[1] = 0;
% Final state: all on destination shore
constraint wolf_pos[num_stages] = 1 /\ goat_pos[num_stages] = 1 /\ cabbage_pos[num_stages] = 1 /\ boat_pos[num_stages] = 1;

% Transitions between stages
constraint forall(s in 1..num_stages-1) (
    % The farmer (and boat) cross each time
    boat_pos[s+1] = 1 - boat_pos[s] /\
    % At most one item can be taken
    take_wolf[s] + take_goat[s] + take_cabbage[s] <= 1 /\
    % Wolf transition
    (take_wolf[s] = 1 -> (wolf_pos[s] = boat_pos[s] /\ wolf_pos[s+1] = boat_pos[s+1])) /\
    (take_wolf[s] = 0 -> wolf_pos[s+1] = wolf_pos[s]) /\
    % Goat transition
    (take_goat[s] = 1 -> (goat_pos[s] = boat_pos[s] /\ goat_pos[s+1] = boat_pos[s+1])) /\
    (take_goat[s] = 0 -> goat_pos[s+1] = goat_pos[s]) /\
    % Cabbage transition
    (take_cabbage[s] = 1 -> (cabbage_pos[s] = boat_pos[s] /\ cabbage_pos[s+1] = boat_pos[s+1])) /\
    (take_cabbage[s] = 0 -> cabbage_pos[s+1] = cabbage_pos[s])
);

% Safety: never leave wolf with goat or goat with cabbage unattended
constraint forall(s in 1..num_stages) (
    not (wolf_pos[s] = goat_pos[s] /\ boat_pos[s] != wolf_pos[s]) /\
    not (goat_pos[s] = cabbage_pos[s] /\ boat_pos[s] != goat_pos[s])
);

solve satisfy;

% Output in JSON format
output [
    "{",
    join(",", [
        "\"wolf_pos\": [" ++ join(",", [show(wolf_pos[s]) | s in 1..num_stages]) ++ "]",
        "\"goat_pos\": [" ++ join(",", [show(goat_pos[s]) | s in 1..num_stages]) ++ "]",
        "\"cabbage_pos\": [" ++ join(",", [show(cabbage_pos[s]) | s in 1..num_stages]) ++ "]",
        "\"boat_pos\": [" ++ join(",", [show(boat_pos[s]) | s in 1..num_stages]) ++ "]"
    ]),
    "}"
];
