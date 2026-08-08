
% Include global constraints library
include "globals.mzn";

% Decision variable: number of apples before gate i (i=0..5, where 0 is start, 5 is after last gate)
array[0..5] of var int: apples;

% Constraints: after the 5th gate, no apples remain
constraint apples[5] = 0;

% For each gate i=1..5, the boy gives half of his apples plus one (integer),
% so apples[i-1] must be even, and the remaining apples is apples[i] = apples[i-1]/2 - 1
constraint
  forall(i in 1..5) (
    apples[i-1] mod 2 = 0 /\
    apples[i] = apples[i-1] div 2 - 1
  );

% All apple counts must be non-negative
constraint forall(i in 0..5)( apples[i] >= 0 );

% Minimize the initial number of apples to find the smallest solution
solve minimize apples[0];

% Output the list of apples before each gate and after the last gate in JSON format
output [
  "{",
  "\"apples\":[" ++ join(",", [show(apples[i]) | i in 0..5]) ++ "]",
  "}"
];
