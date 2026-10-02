% Sports tournament scheduling (CSPLib 26): schedule a tournament of n teams
% over n-1 weeks, each week divided into n/2 periods, and each period into two
% slots (the first team plays at home, the second away). Every team plays once
% a week, every team plays at most twice in the same period over the
% tournament, and every team plays every other team.
include "globals.mzn";

int: n_teams;  % number of teams, numbered 1..n_teams

int: n_weeks = n_teams - 1;
int: n_periods = n_teams div 2;
set of int: Teams = 1..n_teams;
set of int: Weeks = 1..n_weeks;
set of int: Periods = 1..n_periods;

% home[w, p], away[w, p] = the team playing at home / away in period p of week w
array[Weeks, Periods] of var Teams: home;
array[Weeks, Periods] of var Teams: away;

% a team cannot play itself
constraint forall(w in Weeks, p in Periods) (home[w, p] != away[w, p]);

% every team plays once a week: all teams in a week's matches are different
constraint forall(w in Weeks)
    (all_different([home[w, p] | p in Periods] ++ [away[w, p] | p in Periods]));

% every team plays every other team, at home or away. There are exactly as many
% matches as pairs of teams, so each pair meets exactly once; that equality is
% implied by the reference's "at least once" and is stated because Gecode
% prunes more with it.
constraint forall(t1, t2 in Teams where t1 < t2)
    (sum(w in Weeks, p in Periods)
        (bool2int(home[w, p] = t1 /\ away[w, p] = t2) + bool2int(home[w, p] = t2 /\ away[w, p] = t1)) = 1);

% every team plays at most twice in the same period over the tournament
constraint forall(t in Teams, p in Periods)
    (sum(w in Weeks) (bool2int(home[w, p] = t \/ away[w, p] = t)) <= 2);

solve satisfy;

output ["{\"home\": [", join(", ", ["[" ++ join(", ", [show(home[w, p]) | p in Periods]) ++ "]" | w in Weeks]),
        "], \"away\": [", join(", ", ["[" ++ join(", ", [show(away[w, p]) | p in Periods]) ++ "]" | w in Weeks]), "]}"];
