include "globals.mzn";

int: n = 31;
int: coins_per_line = 14;

% Decision variables: x[i,j] = 1 if a coin is placed in cell (i,j), 0 otherwise
array[1..n, 1..n] of var 0..1: x;

% Constraint 1: Each row has exactly 14 coins
constraint
  forall(i in 1..n) (
    sum(j in 1..n)(x[i,j]) == coins_per_line
  );

% Constraint 2: Each column has exactly 14 coins
constraint
  forall(j in 1..n) (
    sum(i in 1..n)(x[i,j]) == coins_per_line
  );

% Objective: minimize sum of squared horizontal distances from main diagonal
% Horizontal distance = abs(j - i)
var int: z = sum(i,j in 1..n)(x[i,j] * (j - i) * (j - i));

solve minimize z;

output [
  "{\n",
  "  \"x\": [\n",
  join(",\n", [ "    " ++ show([x[i,j] | j in 1..n]) | i in 1..n ]),
  "\n  ],\n",
  "  \"z\": ", show(z), "\n",
  "}"
];