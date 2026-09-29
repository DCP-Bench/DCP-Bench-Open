% Water bucket: three buckets with given capacities start in the initial state
% and water is poured from one bucket into another (until the source is empty
% or the target full). Reach the goal state with as few pourings as possible.
% The states are listed one per step in a fixed-length sequence, padded after the goal.
include "globals.mzn";

array[int] of int: capacities;
array[int] of int: initial_state;
array[int] of int: goal_state;
int: MAX_STEPS;      % length of the output sequence
int: PADDING_VALUE;  % marks the unused steps after the goal

set of int: Buckets = index_set(capacities);
int: total_water = sum(initial_state);  % the water is only moved around, never lost

% sequence[t, b] = the amount in bucket b after t pourings, or padding
array[1..MAX_STEPS, Buckets] of var PADDING_VALUE..total_water: sequence;

% a step is padding when its first bucket holds the padding value
array[1..MAX_STEPS] of var bool: padded;
constraint forall(t in 1..MAX_STEPS) (padded[t] <-> sequence[t, min(Buckets)] = PADDING_VALUE);

% is the state at step t the goal
array[1..MAX_STEPS] of var bool: at_goal;
constraint forall(t in 1..MAX_STEPS) (at_goal[t] <-> forall(b in Buckets) (sequence[t, b] = goal_state[b]));

% the sequence starts with the initial state
constraint forall(b in Buckets) (sequence[1, b] = initial_state[b]);

% a state that is not padding keeps all the water and stays within the capacities
constraint forall(t in 1..MAX_STEPS) (not padded[t] -> (
    sum(b in Buckets) (sequence[t, b]) = total_water /\
    forall(b in Buckets) (sequence[t, b] >= 0 /\ sequence[t, b] <= capacities[b])));

constraint forall(t in 1..MAX_STEPS - 1) (
    % the goal is followed by padding
    (at_goal[t] -> forall(b in Buckets) (sequence[t + 1, b] = PADDING_VALUE)) /\
    % once padding starts it goes on
    (padded[t] -> forall(b in Buckets) (sequence[t + 1, b] = PADDING_VALUE)) /\
    % any other step is a pouring from one bucket into another until the source is
    % empty or the target full, and it changes the state
    ((not at_goal[t] /\ not padded[t]) -> exists(src in Buckets, dst in Buckets where src != dst) (
        let { var int: amount = min(sequence[t, src], capacities[dst] - sequence[t, dst]) } in
        amount > 0 /\
        sequence[t + 1, src] = sequence[t, src] - amount /\
        sequence[t + 1, dst] = sequence[t, dst] + amount /\
        forall(b in Buckets where b != src /\ b != dst) (sequence[t + 1, b] = sequence[t, b]))));

% the goal is reached at some step
constraint exists(t in 1..MAX_STEPS) (at_goal[t]);

% cost = number of pourings = number of states before the padding starts, minus one
var int: cost = sum(t in 1..MAX_STEPS) (bool2int(not padded[t])) - 1;
var int: objective = cost;
solve minimize objective;

output ["{\"cost\": ", show(cost), ", \"sequence\": [",
        join(", ", ["[" ++ join(", ", [show(sequence[t, b]) | b in Buckets]) ++ "]" | t in 1..MAX_STEPS]), "]}"];
