include "globals.mzn";

% Input data
int: n_teams = 9;
int: n_days = 18;

% Teams indexed 1..9
% 1: Clem, 2: Duke, 3: FSU, 4: GT, 5: UMD, 6: UNC, 7: NCSt, 8: UVA, 9: Wake

% Mirroring pairs (r1,r2)
array[1..9,1..2] of int: mirroring = array2d(1..9,1..2,
  [1,8, 2,9, 3,12, 4,13, 5,14, 6,15, 7,16, 10,17, 11,18]);

% Rival pairs (team1, team2)
array[1..4,1..2] of int: rivals = array2d(1..4,1..2,
  [2,6, 1,4, 7,9, 5,8]); % Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA

% Days that are weekends (even days)
set of int: weekends = {d | d in 1..n_days where d mod 2 = 0};
set of int: weekdays = {d | d in 1..n_days where d mod 2 = 1};

% Decision variables
% config[d,t] = opponent team or 0 if bye
array[1..n_days, 1..n_teams] of var 0..n_teams: config;

% where[d,t] = 0 bye, 1 home, 2 away
array[1..n_days, 1..n_teams] of var 0..2: where;

% Constraints

% 1) Double round robin: each pair plays twice, once home once away
% For each pair (i<j), must appear exactly twice in config, once i home j away, once j home i away
% Count occurrences of matches
predicate match_occurs(int: d, int: t1, int: t2) =
  (config[d,t1] = t2 /\ where[d,t1] = 1 /\ where[d,t2] = 2);

% Each team plays exactly one match or bye per day
constraint forall(d in 1..n_days) (
  forall(t in 1..n_teams) (
    % config[d,t] = 0 means bye
    % if config[d,t] != 0 then config[d,config[d,t]] = t and where[d,t] != 0
    (config[d,t] = 0 -> where[d,t] = 0) /\
    (config[d,t] != 0 -> (config[d,config[d,t]] = t /\ where[d,t] != 0 /\ where[d,config[d,t]] != 0))
  )
);

% No self matches
constraint forall(d in 1..n_days, t in 1..n_teams) (
  config[d,t] != t
);

% Each pair plays exactly twice, once home once away
constraint forall(t1, t2 in 1..n_teams where t1 < t2) (
  sum(d in 1..n_days)(bool2int(match_occurs(d,t1,t2))) = 1 /\
  sum(d in 1..n_days)(bool2int(match_occurs(d,t2,t1))) = 1
);

% Each team plays exactly one match or bye per day
constraint forall(d in 1..n_days) (
  forall(t in 1..n_teams) (
    (config[d,t] = 0 \/ (config[d,t] != 0 /\ config[d,config[d,t]] = t))
  )
);

% 1) Mirroring scheme: pairs of dates have same matches (same pairs)
% For each mirroring pair (r1,r2), for all teams t: config[r1,t] = config[r2,t]
constraint forall(i in 1..9) (
  let {int: r1 = mirroring[i,1], r2 = mirroring[i,2]} in
  forall(t in 1..n_teams) (
    % config[r1,t] = config[r2,t]
    config[r1,t] = config[r2,t] /\
    % where[r1,t] != where[r2,t] (home/away reversed)
    (where[r1,t] = 1 -> where[r2,t] = 2) /\
    (where[r1,t] = 2 -> where[r2,t] = 1) /\
    (where[r1,t] = 0 -> where[r2,t] = 0)
  )
);

% 2) No two final aways: no team plays away on both last dates (17,18)
constraint forall(t in 1..n_teams) (
  not (where[17,t] = 2 /\ where[18,t] = 2)
);

% 3) Home/Away/Bye pattern constraints
% No more than two away matches in a row
constraint forall(t in 1..n_teams, d in 1..n_days-2) (
  not (where[d,t] = 2 /\ where[d+1,t] = 2 /\ where[d+2,t] = 2)
);
% No more than two home matches in a row
constraint forall(t in 1..n_teams, d in 1..n_days-2) (
  not (where[d,t] = 1 /\ where[d+1,t] = 1 /\ where[d+2,t] = 1)
);
% No more than three away or byes in a row
constraint forall(t in 1..n_teams, d in 1..n_days-3) (
  not (forall(i in d..d+3) (where[i,t] = 2 \/ where[i,t] = 0))
);
% No more than four home or byes in a row
constraint forall(t in 1..n_teams, d in 1..n_days-4) (
  not (forall(i in d..d+4) (where[i,t] = 1 \/ where[i,t] = 0))
);

% 4) Weekend pattern: each team plays 4 home, 4 away, 1 bye on weekends
constraint forall(t in 1..n_teams) (
  sum(d in weekends)(bool2int(where[d,t] = 1)) = 4 /\
  sum(d in weekends)(bool2int(where[d,t] = 2)) = 4 /\
  sum(d in weekends)(bool2int(where[d,t] = 0)) = 1
);

% 5) First weekends: each team has home or bye at least on two of first five weekends
constraint forall(t in 1..n_teams) (
  sum(d in {2,4,6,8,10})(bool2int(where[d,t] = 1 \/ where[d,t] = 0)) >= 2
);

% 6) Rival matches: last date (18), every team except FSU (3) plays rival unless plays FSU or bye
constraint forall(i in 1..4) (
  let {int: t1 = rivals[i,1], t2 = rivals[i,2]} in
  (
    % If t1 plays FSU or bye on day 18, no constraint
    (config[18,t1] = 3 \/ config[18,t1] = 0) \/
    % else t1 plays rival t2 on day 18
    (config[18,t1] = t2)
  ) /\
  (
    (config[18,t2] = 3 \/ config[18,t2] = 0) \/
    (config[18,t2] = t1)
  )
);

% 7) Constrained matches: pairings must occur at least once in dates 11..18
array[1..4,1..2] of int: constrained_pairs = array2d(1..4,1..2,
  [9,6, 9,2, 4,6, 4,2]); % Wake-UNC, Wake-Duke, GT-UNC, GT-Duke

constraint forall(i in 1..4) (
  let {int: t1 = constrained_pairs[i,1], t2 = constrained_pairs[i,2]} in
  sum(d in 11..18)(bool2int(match_occurs(d,t1,t2) \/ match_occurs(d,t2,t1))) >= 1
);

% 8) Opponent sequence constraints
% No team plays in two consecutive dates away against UNC(6) and Duke(2)
constraint forall(t in 1..n_teams) (
  forall(d in 1..n_days-1) (
    not (
      where[d,t] = 2 /\ config[d,t] in {6,2} /\
      where[d+1,t] = 2 /\ config[d+1,t] in {6,2}
    )
  )
);

% No team plays in three consecutive dates against UNC(6), Duke(2), Wake(9) (home/away doesn't matter)
constraint forall(t in 1..n_teams) (
  forall(d in 1..n_days-2) (
    not (
      (config[d,t] in {6,2,9}) /\
      (config[d+1,t] in {6,2,9}) /\
      (config[d+2,t] in {6,2,9})
    )
  )
);

% 9) Other constraints
% UNC(6) plays rival Duke(2) in last date(18) and date 11
constraint config[18,6] = 2 /\ config[11,6] = 2;
% UNC(6) plays Clem(1) in second date(2)
constraint config[2,6] = 1;
% Duke(2) has bye in date 16
constraint config[16,2] = 0 /\ where[16,2] = 0;
% Wake(9) does not play home in date 17
constraint where[17,9] != 1;
% Wake(9) has bye in first date(1)
constraint config[1,9] = 0 /\ where[1,9] = 0;
% Clem(1), Duke(2), UMD(5), Wake(9) do not play away in last date(18)
constraint forall(t in {1,2,5,9}) (
  where[18,t] != 2
);
% Clem(1), FSU(3), GT(4), Wake(9) do not play away in first date(1)
constraint forall(t in {1,3,4,9}) (
  where[1,t] != 2
);
% FSU(3), NCSt(7) have no bye in last date(18)
constraint forall(t in {3,7}) (
  config[18,t] != 0 /\ where[18,t] != 0
);
% UNC(6) does not have bye in first date(1)
constraint config[1,6] != 0 /\ where[1,6] != 0;

% Solve
solve satisfy;

% Output
output [
  "{",
  "\"config\": [",
  join(",\n", [ "[" ++ join(",", [show(config[d,t]) | t in 1..n_teams]) ++ "]" | d in 1..n_days ]),
  "],",
  "\"where\": [",
  join(",\n", [ "[" ++ join(",", [show(where[d,t]) | t in 1..n_teams]) ++ "]" | d in 1..n_days ]),
  "]",
  "}"
];