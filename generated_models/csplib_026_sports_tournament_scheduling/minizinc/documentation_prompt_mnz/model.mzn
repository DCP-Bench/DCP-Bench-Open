include "globals.mzn";

% Input data
int: n_teams = 8;
int: n_weeks = n_teams - 1;
int: n_periods = n_teams div 2;

% Sets
set of int: TEAMS = 0..n_teams-1;
set of int: WEEKS = 1..n_weeks;
set of int: PERIODS = 1..n_periods;
set of int: SLOTS = 1..2; % slot 1: home team, slot 2: away team

% Decision variables:
% home[w,p] = team playing at home in week w, period p
array[WEEKS, PERIODS] of var TEAMS: home;
% away[w,p] = team playing away in week w, period p
array[WEEKS, PERIODS] of var TEAMS: away;

% Constraints

% 1) Every team plays once a week (either home or away)
constraint
  forall(w in WEEKS) (
    forall(t in TEAMS) (
      % team t appears exactly once in week w either home or away
      sum([bool2int(home[w,p] == t) + bool2int(away[w,p] == t) | p in PERIODS]) == 1
    )
  );

% 2) Every team plays at most twice in the same period over the tournament
constraint
  forall(t in TEAMS, p in PERIODS) (
    sum([bool2int(home[w,p] == t) + bool2int(away[w,p] == t) | w in WEEKS]) <= 2
  );

% 3) Every team plays every other team exactly once (round robin)
% For each pair of distinct teams (t1,t2), they must meet exactly once:
constraint
  forall(t1, t2 in TEAMS where t1 < t2) (
    sum([bool2int((home[w,p] == t1 /\ away[w,p] == t2) \/ (home[w,p] == t2 /\ away[w,p] == t1)) | w in WEEKS, p in PERIODS]) == 1
  );

% 4) No team plays against itself
constraint
  forall(w in WEEKS, p in PERIODS) (
    home[w,p] != away[w,p]
  );

% 5) All teams in home and away slots are valid teams (domain already defined by var TEAMS)

% 6) Optional: all pairs in a week are distinct (no repeated matches in same week)
% Already ensured by constraint 1 and 3

% Solve satisfy
solve satisfy;

output [
  "{",
  "\"home\": [",
  join(",\n", [
    "[" ++ join(", ", [show(home[w,p]) | p in PERIODS]) ++ "]" | w in WEEKS
  ]),
  "],",
  "\"away\": [",
  join(",\n", [
    "[" ++ join(", ", [show(away[w,p]) | p in PERIODS]) ++ "]" | w in WEEKS
  ]),
  "]",
  "}"
];