include "globals.mzn";

% Input data
int: v = 9;   % Number of distinct objects
int: b = 12;  % Number of blocks
int: r = 4;   % Number of blocks each object occurs in
int: k = 3;   % Number of objects each block contains
int: l = 1;   % Number of blocks in which each pair of distinct objects occurs together (lambda)

% Decision variable: incidence matrix of size v x b
array[1..v, 1..b] of var 0..1: matrix;

% Constraints

% Each object occurs in exactly r blocks (row sum)
constraint
  forall(i in 1..v) (
    sum(j in 1..b)(matrix[i,j]) == r
  );

% Each block contains exactly k objects (column sum)
constraint
  forall(j in 1..b) (
    sum(i in 1..v)(matrix[i,j]) == k
  );

% For every pair of distinct objects, the scalar product of their rows is exactly l
constraint
  forall(i1, i2 in 1..v where i1 < i2) (
    sum(j in 1..b)(matrix[i1,j] * matrix[i2,j]) == l
  );

solve satisfy;

output [
  "{\n",
  "  \"matrix\": [\n",
  join(",\n", [
    "    [" ++ join(", ", [show(matrix[i,j]) | j in 1..b]) ++ "]"
    | i in 1..v
  ]),
  "\n  ]\n",
  "}"
];