% Progressive party: at a yacht club some boats are hosts and the crews of the
% other boats visit a host in each time period. Choose the hosts and the visit
% schedule so that capacities are respected and the number of hosts is minimal.
include "globals.mzn";

int: n_boats;
int: n_periods;
array[1..n_boats] of int: capacity;   % most people a boat can hold at one time
array[1..n_boats] of int: crew_size;  % people in each boat's crew

set of int: Boats = 1..n_boats;
set of int: Periods = 1..n_periods;

% is_host[b] = true if boat b is a host boat
array[Boats] of var bool: is_host;

% visits[p, b] = the boat whose crew b's crew is on during period p (boats are
% numbered from 1 here and from 0 in the printed output)
array[Periods, Boats] of var Boats: visits;

% the crew of a host boat stays on board in every period
constraint forall(b in Boats) (is_host[b] -> forall(p in Periods) (visits[p, b] = b));

% in each period the crews on a boat (its own crew included if it stays) number
% no more than the boat's capacity
constraint forall(p in Periods, b in Boats)
    (sum(c in Boats) (bool2int(visits[p, c] = b) * crew_size[c]) <= capacity[b]);

% a guest crew cannot visit the same boat twice
constraint forall(b in Boats) (not is_host[b] -> alldifferent([visits[p, b] | p in Periods]));

% a boat that is not a host is never visited
constraint forall(b in Boats) (not is_host[b] -> forall(p in Periods, c in Boats) (visits[p, c] != b));

% two crews meet (are on the same boat in the same period) at most once
constraint forall(c1, c2 in Boats where c1 < c2)
    (sum(p in Periods) (bool2int(visits[p, c1] = visits[p, c2])) <= 1);

% the objective is to use as few host boats as possible
var int: objective = sum(b in Boats) (bool2int(is_host[b]));
solve minimize objective;

output ["{\"visits\": [",
        join(", ", ["[" ++ join(", ", [show(fix(visits[p, b]) - 1) | b in Boats]) ++ "]" | p in Periods]),
        "], \"is_host\": [", join(", ", [show(fix(is_host[b])) | b in Boats]), "]}"];
