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

% assign[g, w] = the group golfer g plays in during week w (groups are numbered
% from 1 here and from 0 in the printed output)
array[Golfers, Weeks] of var Groups: assign;

% each group has exactly group_size players in every week
constraint forall(w in Weeks)
    (global_cardinality([assign[g, w] | g in Golfers], [gr | gr in Groups], [group_size | gr in Groups]));

% each pair of golfers meets (shares a group) in at most one week
constraint forall(g1, g2 in Golfers where g1 < g2)
    (sum(w in Weeks) (bool2int(assign[g1, w] = assign[g2, w])) <= 1);

solve satisfy;

output ["{\"assign\": [",
        join(", ", ["[" ++ join(", ", [show(fix(assign[g, w]) - 1) | w in Weeks]) ++ "]" | g in Golfers]),
        "]}"];
