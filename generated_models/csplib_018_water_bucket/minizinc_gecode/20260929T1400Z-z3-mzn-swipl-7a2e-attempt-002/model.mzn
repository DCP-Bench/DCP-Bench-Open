% Water bucket: three buckets with given capacities start in the initial state
% and water is poured from one bucket into another (until the source is empty
% or the target full). Reach the goal state with as few pourings as possible.
% The states are listed one per step in a fixed-length sequence, padded after the goal.
include "globals.mzn";

array[int] of int: capacities;   % the problem has three buckets
array[int] of int: initial_state;
array[int] of int: goal_state;
int: MAX_STEPS;      % length of the output sequence
int: PADDING_VALUE;  % marks the unused steps after the goal

int: total_water = sum(initial_state);  % the water is only moved around, never lost

% Every state within the capacities that holds all the water, as a flat list of
% (bucket 1, bucket 2, bucket 3) triples, and helpers to read them.
array[int] of int: states_flat = [
    if k = 1 then a elseif k = 2 then b else total_water - a - b endif
    | a in 0..capacities[1], b in 0..capacities[2], k in 1..3
      where total_water - a - b >= 0 /\ total_water - a - b <= capacities[3]];
int: n_states = length(states_flat) div 3;
function int: state(int: s, int: bucket) = states_flat[(s - 1) * 3 + bucket];
function bool: is_goal(int: s) = forall(b in 1..3) (state(s, b) = goal_state[b]);
% how much a pouring from bucket src into bucket dst moves: until the source is
% empty or the target full
function int: moved(int: s, int: src, int: dst) = min(state(s, src), capacities[dst] - state(s, dst));

% Every legal pouring from a state that is not the goal, as a row of six numbers:
% the state before and the state after.
array[int] of int: pourings_flat = [
    if m <= 3 then state(s, m)
    elseif m - 3 = src then state(s, m - 3) - moved(s, src, dst)
    elseif m - 3 = dst then state(s, m - 3) + moved(s, src, dst)
    else state(s, m - 3) endif
    | s in 1..n_states, src in 1..3, dst in 1..3, m in 1..6
      where src != dst /\ moved(s, src, dst) > 0 /\ not is_goal(s)];

% One step of the sequence is a pouring from a state that is not the goal, a move
% from the goal into the padding, or padding after padding.
array[int] of int: padding = [PADDING_VALUE, PADDING_VALUE, PADDING_VALUE];
array[int] of int: transitions_flat = pourings_flat ++ goal_state ++ padding ++ padding ++ padding;
array[1..length(transitions_flat) div 6, 1..6] of int: transitions =
    array2d(1..length(transitions_flat) div 6, 1..6, transitions_flat);

% sequence[t, b] = the amount in bucket b after t pourings, or padding
array[1..MAX_STEPS, 1..3] of var PADDING_VALUE..total_water: sequence;

% the sequence starts with the initial state
constraint forall(b in 1..3) (sequence[1, b] = initial_state[b]);

% each step follows from the one before by an allowed transition
constraint forall(t in 1..MAX_STEPS - 1) (
    table([sequence[t, b] | b in 1..3] ++ [sequence[t + 1, b] | b in 1..3], transitions));

% the last step is the goal or padding, so the goal has been reached at some point
constraint table([sequence[MAX_STEPS, b] | b in 1..3], array2d(1..2, 1..3, goal_state ++ padding));

% cost = number of pourings = number of states before the padding starts, minus one
var int: cost = sum(t in 1..MAX_STEPS) (bool2int(sequence[t, 1] != PADDING_VALUE)) - 1;
var int: objective = cost;
solve minimize objective;

output ["{\"cost\": ", show(cost), ", \"sequence\": [",
        join(", ", ["[" ++ join(", ", [show(sequence[t, b]) | b in 1..3]) ++ "]" | t in 1..MAX_STEPS]), "]}"];
