include "globals.mzn";

% Input data
int: n_weeks = 4;      % Number of weeks
int: n_groups = 3;     % Number of groups per week
int: group_size = 3;   % Number of golfers per group
int: n_golfers = n_groups * group_size; % Total number of golfers

% Decision variable:
% assign[w,g,p] = golfer assigned to position p in group g in week w
array[1..n_weeks, 1..n_groups, 1..group_size] of var 1..n_golfers: assign;

% Constraints

% 1) Each group in each week has distinct golfers
constraint
  forall(w in 1..n_weeks, g in 1..n_groups) (
    alldifferent([assign[w,g,p] | p in 1..group_size])
  );

% 2) Each golfer plays exactly once per week (no golfer appears twice in the same week)
constraint
  forall(w in 1..n_weeks) (
    alldifferent([assign[w,g,p] | g in 1..n_groups, p in 1..group_size])
  );

% 3) No pair of golfers plays together more than once across all weeks and groups
% For every pair of distinct golfers (g1,g2), they can appear together at most once
% We check all pairs of golfers and count the number of times they appear together

% To implement this efficiently, we create a boolean variable for each pair and each week/group
% indicating if the pair appears together in that group in that week

array[1..n_golfers, 1..n_golfers, 1..n_weeks, 1..n_groups] of var bool: pair_in_group;

% Define pair_in_group variables
constraint
  forall(w in 1..n_weeks, g in 1..n_groups, i in 1..n_golfers, j in i+1..n_golfers) (
    pair_in_group[i,j,w,g] <-> (
      % i and j both appear in assign[w,g,*]
      (exists(p1 in 1..group_size)(assign[w,g,p1] = i) /\
       exists(p2 in 1..group_size)(assign[w,g,p2] = j))
    )
  );

% For pairs where i >= j, pair_in_group[i,j,w,g] = false (no self pairs or reversed)
constraint
  forall(w in 1..n_weeks, g in 1..n_groups, i in 1..n_golfers, j in 1..i) (
    pair_in_group[i,j,w,g] = false
  );

% Sum over all weeks and groups for each pair <= 1
constraint
  forall(i,j in 1..n_golfers where i < j) (
    sum([bool2int(pair_in_group[i,j,w,g]) | w in 1..n_weeks, g in 1..n_groups]) <= 1
  );

% Solve: find any feasible schedule
solve satisfy;

% Output the assignments as a 3D array: assign[w][g][p]
output [
  "{",
  "\"assign\": [",
  concat([
    "["
    ++ concat([
      "["
      ++ concat([
        show(assign[w,g,p]) ++ if p < group_size then "," else "" endif
        | p in 1..group_size
      ])
      ++ "]" ++ if g < n_groups then "," else "" endif
      | g in 1..n_groups
    ])
    ++ "]" ++ if w < n_weeks then "," else "" endif
    | w in 1..n_weeks
  ]),
  "]",
  "}"
];