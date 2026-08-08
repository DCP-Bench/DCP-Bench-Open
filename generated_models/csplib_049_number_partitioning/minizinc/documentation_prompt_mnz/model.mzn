include "globals.mzn";

% Input data
int: n = 12;

% Check feasibility conditions
constraint n >= 8;
constraint n mod 4 = 0;

% Sets of numbers
set of int: NUMS = 1..n;

% Decision variables: assign each number to set A (true) or B (false)
array[NUMS] of var bool: inA;

% Cardinality constraint: A and B have the same size
constraint sum([bool2int(inA[i]) | i in NUMS]) = n div 2;

% Sum constraints
constraint sum([i * bool2int(inA[i]) | i in NUMS]) = sum([i * (1 - bool2int(inA[i])) | i in NUMS]);

% Sum of squares constraints
constraint sum([i*i * bool2int(inA[i]) | i in NUMS]) = sum([i*i * (1 - bool2int(inA[i])) | i in NUMS]);

% Extract sets A and B from inA
array[1..n div 2] of var int: A;
array[1..n div 2] of var int: B;

% Assign values to A and B arrays
% We use the fact that A contains exactly n/2 elements assigned true in inA
% and B contains the rest
constraint
  % A contains all numbers i where inA[i] = true
  % B contains all numbers i where inA[i] = false
  % We enforce that A and B are sorted to avoid symmetry
  forall(i in 1..n div 2) (
    A[i] in NUMS /\
    B[i] in NUMS
  ) /\
  increasing(A) /\
  increasing(B);

% Link A and B arrays with inA
% For each number i, if inA[i] = true then i is in A, else in B
% We enforce that A and B are exactly the partition of 1..n
constraint
  forall(i in NUMS) (
    (inA[i] -> (exists(j in 1..n div 2)(A[j] = i))) /\
    (not inA[i] -> (exists(j in 1..n div 2)(B[j] = i)))
  );

% Ensure A and B are disjoint and cover all numbers
constraint
  forall(i,j in 1..n div 2 where i != j) (
    A[i] != A[j] /\ B[i] != B[j]
  ) /\
  forall(i in 1..n div 2, j in 1..n div 2) (
    A[i] != B[j]
  );

solve satisfy;

output [
  "{",
  "\"A\": ", show(A), ",",
  "\"B\": ", show(B),
  "}"
];