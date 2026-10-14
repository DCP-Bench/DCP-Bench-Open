% Sports tournament scheduling: n teams play over n-1 weeks, each week has n/2
% periods, and a period holds one match (a home team and an away team). Every
% team plays once a week, at most twice in the same period over the whole
% tournament, and meets every other team. Teams are numbered 1..n.
include "globals.mzn";

int: n_teams;
int: n_weeks = n_teams - 1;
int: n_periods = n_teams div 2;

% home[w, p], away[w, p] = the team number in the slot
array[1..n_weeks, 1..n_periods] of var 1..n_teams: home;
array[1..n_weeks, 1..n_periods] of var 1..n_teams: away;

% a team does not play itself
constraint forall(w in 1..n_weeks, p in 1..n_periods) (home[w, p] != away[w, p]);

% every team plays exactly once a week: the n slots of a week (home and away,
% all periods) hold n different teams
constraint forall(w in 1..n_weeks) (
    all_different([home[w, p] | p in 1..n_periods] ++ [away[w, p] | p in 1..n_periods]));

% every team meets every other team at least once, at home or away
constraint forall(t1, t2 in 1..n_teams where t1 < t2) (
    sum(w in 1..n_weeks, p in 1..n_periods) (
        bool2int((home[w, p] = t1 /\ away[w, p] = t2) \/ (home[w, p] = t2 /\ away[w, p] = t1))) >= 1);

% a team plays at most twice in the same period over the tournament
constraint forall(t in 1..n_teams, p in 1..n_periods) (
    sum(w in 1..n_weeks) (bool2int(home[w, p] = t \/ away[w, p] = t)) <= 2);

solve satisfy;

output ["{\"home\": [",
        join(", ", ["[" ++ join(", ", [show(home[w, p]) | p in 1..n_periods]) ++ "]" | w in 1..n_weeks]),
        "], \"away\": [",
        join(", ", ["[" ++ join(", ", [show(away[w, p]) | p in 1..n_periods]) ++ "]" | w in 1..n_weeks]), "]}"];
