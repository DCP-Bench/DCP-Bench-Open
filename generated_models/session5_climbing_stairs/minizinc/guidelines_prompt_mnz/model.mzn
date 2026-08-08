
% Include global constraints library
include "globals.mzn";

% Input data
int: n = 20;           % total number of steps to climb
int: m1 = 3;           % minimum step size
int: m2 = 5;           % maximum step size
int: max_moves = 20;   % we allow at most 20 moves (will pad with zeros)

% Decision variables: steps taken at each move (0 means no move)
array[1..max_moves] of var 0..m2: steps;

% Constraints

% 1) Each move is either 0 (no move) or one of the allowed step sizes {3,4,5}
constraint forall(i in 1..max_moves) (
    steps[i] == 0 \/ steps[i] == m1 \/ steps[i] == m1+1 \/ steps[i] == m2
);

% 2) Total sum of steps must equal exactly n
constraint sum(i in 1..max_moves)(steps[i]) = n;

% 3) Once we stop moving (a zero), all subsequent moves must be zero 
constraint forall(i in 1..max_moves-1) (
    steps[i] == 0 -> steps[i+1] == 0
);

% Solve: we only need one feasible sequence
solve satisfy;

% Output in JSON format
output [
    "{",
    "\"steps\": [" ++ join(",", [show(steps[i]) | i in 1..max_moves]) ++ "]",
    "}"
];
