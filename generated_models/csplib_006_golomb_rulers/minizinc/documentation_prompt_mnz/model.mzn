include "globals.mzn";

% Input data
int: size = 10; % Number of marks on the Golomb ruler

% Decision variables
% marks[i] represents the position of the i-th mark on the ruler
array[1..size] of var 0..10000: marks;

% The length of the Golomb ruler is the position of the last mark
var 0..10000: length = marks[size];

% Constraints

% The first mark is at position 0
constraint marks[1] = 0;

% Marks are strictly increasing
constraint forall(i in 1..size-1) (
    marks[i] < marks[i+1]
);

% All differences a_j - a_i for 1 <= i < j <= size are distinct
% Collect all differences in an array
array[1..(size*(size-1)) div 2] of var int: diffs;
var int: idx = 1;
constraint
  forall(i,j in 1..size where i < j) (
    diffs[idx] = marks[j] - marks[i] /\
    idx = idx + 1
  );

% The above cannot be done directly because idx is a var, so we build diffs with a comprehension
% Instead, we build diffs with a comprehension:
array[1..(size*(size-1)) div 2] of var int: diffs2 = 
  [marks[j] - marks[i] | i,j in 1..size where i < j];

constraint all_different(diffs2);

% Symmetry breaking: first difference < last difference
constraint (marks[2] - marks[1]) < (marks[size] - marks[size-1]);

% Objective: minimize the length of the ruler
solve minimize length;

output [
    "{",
    "\"marks\": ", show(marks), ",",
    "\"length\": ", show(length),
    "}"
];