% Social golfers: golfers play once a week in groups of equal size. Schedule n_weeks
% weeks so that no two golfers are in the same group on more than one occasion.
include "globals.mzn";

int: n_weeks;
int: n_groups;
int: group_size;  % number of golfers in each group

int: n_golfers = n_groups * group_size;  % every golfer plays every week

set of int: Golfers = 1..n_golfers;
set of int: Weeks = 1..n_weeks;
set of int: Groups = 1..n_groups;

% Each group is stated as the set of golfers in it, which Gecode propagates
% natively; assign below gives the group number of each golfer, as asked for.
% players[w, k] = the golfers who play in group k in week w
array[Weeks, Groups] of var set of Golfers: players;

% in every week the groups split the golfers: each golfer is in exactly one group
constraint forall(w in Weeks) (partition_set([players[w, k] | k in Groups], Golfers));

% each group has exactly group_size players in every week
constraint forall(w in Weeks, k in Groups) (card(players[w, k]) = group_size);

% two golfers never share a group in two different weeks: groups of different
% weeks have at most one golfer in common (groups of the same week are disjoint)
constraint forall(w1, w2 in Weeks where w1 < w2, k1, k2 in Groups)
    (card(players[w1, k1] intersect players[w2, k2]) <= 1);

% assign[g, w] = the group golfer g plays in during week w (groups are numbered
% from 1 here and from 0 in the printed output)
array[Golfers, Weeks] of var Groups: assign;
constraint forall(g in Golfers, w in Weeks, k in Groups) (assign[g, w] = k <-> g in players[w, k]);

solve satisfy;

output ["{\"assign\": [",
        join(", ", ["[" ++ join(", ", [show(fix(assign[g, w]) - 1) | w in Weeks]) ++ "]" | g in Golfers]),
        "]}"];
