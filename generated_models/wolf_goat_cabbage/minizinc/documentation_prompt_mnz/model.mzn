include "globals.mzn";

% Input data
int: stage = 8;

% We represent positions as 0 (starting shore) or 1 (destination shore)
% Variables: arrays of length 'stage' for each entity
array[1..stage] of var 0..1: wolf_pos;
array[1..stage] of var 0..1: goat_pos;
array[1..stage] of var 0..1: cabbage_pos;
array[1..stage] of var 0..1: boat_pos;

% Helper function to check if two entities are on the same shore
function var bool: same_shore(var int: a, var int: b) = (a == b);

% Constraints

% Initial positions: all on starting shore (0)
constraint wolf_pos[1] = 0;
constraint goat_pos[1] = 0;
constraint cabbage_pos[1] = 0;
constraint boat_pos[1] = 0;

% Final positions: all on destination shore (1)
constraint wolf_pos[stage] = 1;
constraint goat_pos[stage] = 1;
constraint cabbage_pos[stage] = 1;
constraint boat_pos[stage] = 1;

% At each stage, the boat can move or stay, but must carry at most one item with the farmer
% The farmer is represented by the boat position
% Between consecutive stages, the boat moves from one shore to the other (0->1 or 1->0)
% The item moved (if any) must be on the same shore as the boat at the previous stage and move with the boat

% For each step from t to t+1:
% - boat_pos[t+1] != boat_pos[t] (boat crosses the river)
% - either no item moves (only farmer crosses alone), or exactly one item moves with the boat
% - items not moved stay on their shore

constraint forall(t in 1..stage-1) (
    % Boat crosses the river
    boat_pos[t+1] != boat_pos[t] /\
    (
        % No item moves: all items stay, only boat moves
        (
            wolf_pos[t+1] = wolf_pos[t] /\
            goat_pos[t+1] = goat_pos[t] /\
            cabbage_pos[t+1] = cabbage_pos[t]
        )
        \/
        % Exactly one item moves with the boat
        (
            % Wolf moves with boat
            (wolf_pos[t+1] = boat_pos[t+1] /\
             wolf_pos[t] = boat_pos[t] /\
             goat_pos[t+1] = goat_pos[t] /\
             cabbage_pos[t+1] = cabbage_pos[t])
            \/
            % Goat moves with boat
            (goat_pos[t+1] = boat_pos[t+1] /\
             goat_pos[t] = boat_pos[t] /\
             wolf_pos[t+1] = wolf_pos[t] /\
             cabbage_pos[t+1] = cabbage_pos[t])
            \/
            % Cabbage moves with boat
            (cabbage_pos[t+1] = boat_pos[t+1] /\
             cabbage_pos[t] = boat_pos[t] /\
             wolf_pos[t+1] = wolf_pos[t] /\
             goat_pos[t+1] = goat_pos[t])
        )
    )
);

% Safety constraints: at any stage, if the farmer is not on the same shore as the goat,
% then the wolf and goat cannot be left alone together on the same shore (wolf would eat goat)
% and the goat and cabbage cannot be left alone together on the same shore (goat would eat cabbage)

constraint forall(t in 1..stage) (
    % If farmer not with goat, wolf and goat cannot be on same shore
    (goat_pos[t] != boat_pos[t]) -> (wolf_pos[t] != goat_pos[t])
    /\
    % If farmer not with goat, goat and cabbage cannot be on same shore
    (goat_pos[t] != boat_pos[t]) -> (goat_pos[t] != cabbage_pos[t])
);

solve satisfy;

output [
    "{",
    join(",", [
        "\"wolf_pos\": " ++ show(wolf_pos),
        "\"goat_pos\": " ++ show(goat_pos),
        "\"cabbage_pos\": " ++ show(cabbage_pos),
        "\"boat_pos\": " ++ show(boat_pos)
    ]),
    "}"
];