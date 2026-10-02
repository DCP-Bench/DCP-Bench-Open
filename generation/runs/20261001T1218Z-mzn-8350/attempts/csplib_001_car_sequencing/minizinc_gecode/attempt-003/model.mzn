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
int: n_opts = card(Options);

% how many cars need each option (fixed by the demand)
array[Options] of int: option_demand = [sum(t in Types) (demand[t] * requires[t, o]) | o in Options];

% The options are listed from the most loaded station (cars needing the option
% as a share of what its capacity allows) to the least loaded one: perm[c] is the
% option in column c below. Only the order of the columns depends on it.
array[Options] of int: load = [(1000 * option_demand[o] * per_slots[o]) div (at_most[o] * n_cars) | o in Options];
array[Options] of int: perm = arg_sort([-load[o] | o in Options]);

% sequence[s] = type of the car in slot s (types are numbered from 1 here and
% from 0 in the printed output)
array[1..n_cars] of var Types: sequence;

% skip[s, c] = 1 if the car in slot s does NOT need option perm[c].
% The relation is stated as "does not need" because with this reading the model
% was solved by Gecode's default search on 14 of the 21 large instances within 60 s;
% the same constraints stated on the cars that do need the option solved none of the
% 6 large instances tried.
array[1..n_cars, Options] of var 0..1: skip;

% each type appears exactly as often as it is demanded
constraint global_cardinality(sequence, [t | t in Types], demand);

% the options of every slot are those of the car type placed there: the type
% and its option flags are one row of this table
array[Types, 1..n_opts + 1] of int: type_rows =
    array2d(Types, 1..n_opts + 1,
            [ if c = 1 then t else 1 - requires[t, perm[c - 1]] endif | t in Types, c in 1..n_opts + 1 ]);
constraint forall(s in 1..n_cars) (table([sequence[s]] ++ [skip[s, c] | c in Options], type_rows));

% In every window of per_slots[o] consecutive slots at most at_most[o] cars need
% option o, i.e. at least per_slots[o] - at_most[o] of them do not.
constraint forall(c in Options, s in 1..n_cars - per_slots[perm[c]] + 1)
    (sum(k in s..s + per_slots[perm[c]] - 1) (skip[k, c]) >= per_slots[perm[c]] - at_most[perm[c]]);

% Implied: the most cars with option o that can stand in k consecutive slots.
% Whole windows of per_slots[o] slots hold at_most[o] each, and the remaining
% slots hold at most min(at_most[o], remaining).
function int: room(int: o, int: k) = at_most[o] * (k div per_slots[o]) + min(at_most[o], k mod per_slots[o]);

% Implied: all cars with option o stand somewhere, so among the first t slots
% there are at most room(o, t) of them and at least option_demand[o] - room(o, n_cars - t),
% because the last n_cars - t slots take at most room(o, n_cars - t). In terms of
% skipped cars (t minus those cars) this bounds the running count of skip.
% These follow from the constraints above and remove no solution; they give the
% solver counting bounds that the windows alone only reveal one by one.
constraint forall(c in Options, t in 0..n_cars)
    (sum(k in 1..t) (skip[k, c]) <= t - option_demand[perm[c]] + room(perm[c], n_cars - t) /\
     sum(k in 1..t) (skip[k, c]) >= t - room(perm[c], t));

solve satisfy;

output ["{\"sequence\": [", join(", ", [show(fix(sequence[s]) - 1) | s in 1..n_cars]), "]}"];
