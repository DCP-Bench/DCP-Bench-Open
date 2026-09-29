% Rehearsal problem: order the pieces of a concert for rehearsal so that the
% total time players spend present but not playing is minimal. A player arrives
% just before the first piece they play in and leaves after the last one.
include "globals.mzn";

int: num_pieces;
int: num_players;
array[int] of int: duration;         % rehearsal time of each piece
array[int, int] of int: rehearsal;   % rehearsal[p, j] = 1 if player p plays in piece j

% rehearsal_order[i] = the piece rehearsed in slot i, numbered from 0 as in the
% answer (piece j is entry j + 1 of the data); each piece is rehearsed exactly once
array[1..num_pieces] of var 0..num_pieces - 1: rehearsal_order;
constraint all_different(rehearsal_order);

% arrival[p] / departure[p] = first / last slot in which player p is present
array[1..num_players] of var 1..num_pieces: arrival;
array[1..num_players] of var 1..num_pieces: departure;

% a player who plays in slot i must be present in it
constraint forall(p in 1..num_players, i in 1..num_pieces) (
    rehearsal[p, rehearsal_order[i] + 1] = 1 -> (arrival[p] <= i /\ i <= departure[p]));

% waiting = present but not playing; it costs the length of the piece in that slot
var int: objective = sum(p in 1..num_players, i in 1..num_pieces) (
    duration[rehearsal_order[i] + 1]
    * bool2int(arrival[p] <= i /\ i <= departure[p] /\ rehearsal[p, rehearsal_order[i] + 1] = 0));

% minimise the total time players spend waiting
solve minimize objective;

output ["{\"rehearsal_order\": [", join(", ", [show(rehearsal_order[i]) | i in 1..num_pieces]), "]}"];
