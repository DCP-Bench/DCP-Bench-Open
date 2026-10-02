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

solve satisfy;

output ["{\"sequence\": [", join(", ", [show(fix(sequence[s]) - 1) | s in 1..n_cars]), "]}"];
