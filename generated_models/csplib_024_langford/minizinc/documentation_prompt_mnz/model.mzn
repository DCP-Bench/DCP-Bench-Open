include "globals.mzn";

% Input data
int: k = 4; % Number of sets
int: n = 4; % Numbers from 1 to n

% The length of the sequence is k * n
int: length = k * n;

% Decision variables
% solution[i] is the number at position i in the sequence
array[1..length] of var 1..n: solution;

% position[m, s] is the position of the s-th occurrence of number m in the sequence
array[1..n, 1..k] of var 1..length: position;

% Constraints

% 1) All positions must be distinct
constraint
  alldifferent([position[m, s] | m in 1..n, s in 1..k]);

% 2) The solution array must be consistent with the positions
constraint
  forall(m in 1..n, s in 1..k) (
    solution[position[m, s]] = m
  );

% 3) For each number m, the k occurrences must be spaced exactly m numbers apart
% That means for s in 1..k-1: position[m, s+1] = position[m, s] + m + 1
constraint
  forall(m in 1..n, s in 1..k-1) (
    position[m, s+1] = position[m, s] + m + 1
  );

% 4) Positions must be within the sequence length
constraint
  forall(m in 1..n, s in 1..k) (
    position[m, s] <= length
  );

% Solve satisfy
solve satisfy;

% Output the positions and the solution sequence in JSON format
output [
  "{",
  "\"position\": [",
    join(", ", [
      "[" ++ join(", ", [show(position[m, s]) | s in 1..k]) ++ "]"
      | m in 1..n
    ]),
  "],",
  "\"solution\": ", show(solution),
  "}"
];