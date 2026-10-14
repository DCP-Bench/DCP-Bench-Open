% Car sequencing: order the cars on an assembly line so that no station
% (one per option, e.g. air-conditioning or sunroof) is asked to fit more
% cars with its option than its capacity allows within any run of consecutive slots.
include "globals.mzn";

array[int] of int: at_most;    % a station can fit at most this many cars with its option ...
array[int] of int: per_slots;  % ... in any run of this many consecutive slots
array[int] of int: demand;     % how many cars of each type must be built
array[int, int] of int: requires;  % requires[t, o] = 1 if type t needs option o

set of int: Options = index_set(at_most);
set of int: Types = index_set(demand);
int: n_cars = sum(demand);     % total number of slots on the line

% sequence[s] = type of the car in slot s (types are numbered from 1 here and
% from 0 in the printed output)
array[1..n_cars] of var Types: sequence;

% setup[s, o] = 1 if the car in slot s needs option o, read off its type
array[1..n_cars, Options] of var 0..1: setup;

% each type appears exactly as often as it is demanded
constraint global_cardinality(sequence, [t | t in Types], demand);

% the options of every slot are those required by the car type placed there
constraint forall(s in 1..n_cars, o in Options) (setup[s, o] = requires[sequence[s], o]);

% in every window of per_slots[o] consecutive slots, at most at_most[o] cars need option o
constraint forall(o in Options, s in 1..n_cars - per_slots[o] + 1)
    (sum(k in s..s + per_slots[o] - 1) (setup[k, o]) <= at_most[o]);

% Implied: how many cars with option o can stand in k consecutive slots at
% most. Whole windows of per_slots[o] slots hold at_most[o] each, and the
% remaining slots hold at most min(at_most[o], remaining).
function int: room(int: o, int: k) = at_most[o] * (k div per_slots[o]) + min(at_most[o], k mod per_slots[o]);

% Implied: all cars with option o (their number is fixed by the demand) have to
% stand somewhere, so among the first t slots there are at most room(o, t) of
% them and, because the last n_cars - t slots take at most room(o, n_cars - t),
% at least demand_o - room(o, n_cars - t) of them. These follow from the
% constraints above, remove no solution and give the solver counting bounds it
% cannot derive from the windows one by one.
array[Options] of int: option_demand = [sum(t in Types) (demand[t] * requires[t, o]) | o in Options];
array[Options, 0..n_cars] of var int: so_far;  % so_far[o, t] = cars with option o in slots 1..t
constraint forall(o in Options) (so_far[o, 0] = 0);
constraint forall(o in Options, t in 1..n_cars) (so_far[o, t] = so_far[o, t - 1] + setup[t, o]);
constraint forall(o in Options, t in 0..n_cars)
    (so_far[o, t] >= option_demand[o] - room(o, n_cars - t) /\ so_far[o, t] <= room(o, t));

% Search: fill the line from the first slot, trying the highest-numbered type
% first. Without this Gecode's default search does not finish the 200-car
% instances (measured: no solution in 60 s on instance json:1 for the same constraints).
solve :: int_search(sequence, input_order, indomain_max) satisfy;

output ["{\"sequence\": [", join(", ", [show(fix(sequence[s]) - 1) | s in 1..n_cars]), "]}"];
