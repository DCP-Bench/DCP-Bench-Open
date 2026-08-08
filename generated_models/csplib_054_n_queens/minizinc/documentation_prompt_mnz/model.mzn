include "globals.mzn";

% Input data
int: n = 10;

% Decision Variables
% queens[c] = r means the queen in column c is placed in row r
array[1..n] of var 1..n: queens;

% Constraints
% 1) All queens must be in different rows
constraint all_different(queens);

% 2) No two queens share the same diagonal
% For all pairs of columns c1 < c2:
% abs(queens[c1] - queens[c2]) != abs(c1 - c2)
constraint
  forall(c1, c2 in 1..n where c1 < c2) (
    abs(queens[c1] - queens[c2]) != abs(c1 - c2)
  );

solve satisfy;

output [
    "{",
    "\"queens\": [", join(", ", [show(queens[c]) | c in 1..n]), "]",
    "}"
];