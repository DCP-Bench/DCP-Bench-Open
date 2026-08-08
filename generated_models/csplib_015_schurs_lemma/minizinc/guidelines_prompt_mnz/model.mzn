
% Schur's Lemma for n balls into c boxes
% We assign each ball i a box number balls[i] in 1..c
include "globals.mzn";

int: n = 13;            % Number of balls
int: c = 3;             % Number of boxes

% Decision variables: box assignment for each ball
array[1..n] of var 1..c: balls;

% Constraints:
% For any x+y = z, not all three can be in the same box j
constraint
  forall(x, y in 1..n where x + y <= n, j in 1..c) (
    not (balls[x] == j /\ balls[y] == j /\ balls[x+y] == j)
  );

solve satisfy;

% Output the assignment as JSON: "balls": [b1, b2, ..., bn]
output [
  "{",
    "\"balls\":[" ++ join(",", [ show(balls[i]) | i in 1..n ]) ++ "]",
  "}"
];
