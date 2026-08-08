% Climbing stairs problem
% We want to climb a stair of 20 steps with steps taken at each move in [3,5].
% After reaching the top, remaining moves are 0.

int: n = 20; % total steps
int: m1 = 3; % minimum steps per move
int: m2 = 5; % maximum steps per move
int: max_moves = n; % maximum number of moves (worst case all 1 step, but here steps >=3, so max_moves = n is safe)

% Decision variables: steps taken at each move, 0 if no steps taken (after reaching top)
array[1..max_moves] of var 0..m2: steps;

% Constraint: each step is either 0 or between m1 and m2
constraint forall(i in 1..max_moves) (
    steps[i] = 0 \/ (steps[i] >= m1 /\ steps[i] <= m2)
);

% Constraint: sum of steps equals n
constraint sum(i in 1..max_moves)(steps[i]) = n;

% Constraint: once a 0 step is taken, all subsequent steps must be 0 (no more moves after reaching top)
constraint forall(i in 1..max_moves-1) (
    (steps[i] = 0) -> (steps[i+1] = 0)
);

solve satisfy;

output [
    "{",
    "\"steps\": ", show(steps),
    "}"
];