include "globals.mzn";

% Input data
int: n = 13; % Number of balls
int: c = 3;  % Number of boxes

% Decision variables
% balls[i] = j means ball i is in box j
array[1..n] of var 1..c: balls;

% Constraints

% Each ball must be in exactly one box (already ensured by domain of balls)

% For each triple (x,y,z) with x + y = z, and for each box j,
% not all three balls are in the same box
constraint
  forall(x, y in 1..n where x <= y /\ x + y <= n) (
    forall(j in 1..c) (
      % sum of balls[x], balls[y], balls[z] in box j <= 2
      % translate to: count how many of balls[x], balls[y], balls[z] equal j <= 2
      let {
        int: z = x + y
      } in
      (bool2int(balls[x] == j) + bool2int(balls[y] == j) + bool2int(balls[z] == j)) <= 2
    )
  );

solve satisfy;

output [
  "{",
  "\"balls\": ", show(balls),
  "}"
];