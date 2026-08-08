include "globals.mzn";

% Input data
int: n_boats = 5;          % Number of boats
int: n_periods = 4;        % Number of periods
array[1..n_boats] of int: capacity = [6, 8, 12, 12, 12];  % Capacities of the boats
array[1..n_boats] of int: crew_size = [2, 2, 2, 2, 4];   % Crew sizes of the boats

% Decision variables
array[1..n_boats] of var bool: is_host; 
% is_host[b] = true if boat b is a host boat

% visits[p,b] = host boat visited by boat b at period p
% For host boats, visits[p,b] = b (they stay on their own boat)
array[1..n_periods, 1..n_boats] of var 1..n_boats: visits;

% Constraints

% 1) Hosts visit themselves at all periods
constraint
  forall(b in 1..n_boats, p in 1..n_periods) (
    is_host[b] -> (visits[p,b] = b)
  );

% 2) Guests visit only host boats
constraint
  forall(b in 1..n_boats, p in 1..n_periods) (
    not is_host[b] -> is_host[visits[p,b]]
  );

% 3) Hosts do not visit other boats (already ensured by 1)

% 4) A guest boat cannot visit the same host more than once
constraint
  forall(b in 1..n_boats where not is_host[b]) (
    alldifferent([visits[p,b] | p in 1..n_periods])
  );

% 5) Capacity constraints: For each boat and period, total people aboard <= capacity
% Total people aboard = host crew + sum of guest crews visiting that host at that period
constraint
  forall(h in 1..n_boats, p in 1..n_periods) (
    let {
      var int: total_guests = sum(b in 1..n_boats where b != h) (
        bool2int(visits[p,b] = h) * crew_size[b]
      )
    } in
      total_guests + (is_host[h] ? crew_size[h] : 0) <= capacity[h]
  );

% 6) Guests cannot meet more than once: no two guest boats meet more than once
% Two guest boats meet if they visit the same host at the same period
% For each pair of distinct guest boats, the number of periods they meet <= 1
constraint
  forall(b1, b2 in 1..n_boats where b1 < b2 /\ not is_host[b1] /\ not is_host[b2]) (
    sum(p in 1..n_periods) (bool2int(visits[p,b1] = visits[p,b2])) <= 1
  );

% 7) A host boat must be visited by at least one guest boat at some period (to avoid trivial hosts)
constraint
  forall(h in 1..n_boats) (
    is_host[h] -> exists(p in 1..n_periods, b in 1..n_boats where not is_host[b]) (
      visits[p,b] = h
    )
  );

% Objective: minimize number of hosts
solve minimize sum(b in 1..n_boats)(bool2int(is_host[b]));

% Output the visit schedule and host designations in JSON format
output [
  "{",
  "\"visits\": [",
  join(",\n", [
    "[" ++ join(",", [show(visits[p,b]) | b in 1..n_boats]) ++ "]"
    | p in 1..n_periods
  ]),
  "],",
  "\"is_host\": ", show(is_host),
  "}"
];