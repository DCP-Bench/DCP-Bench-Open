include "globals.mzn";

% Number of holes
int: num_holes = 18;

% Possible lengths for each hole
set of int: hole_lengths = {3,4,5};

% Decision variables: length of each hole
array[1..num_holes] of var hole_lengths: holes;

% Constraint: total length of the course is 72
constraint sum(holes) = 72;

solve satisfy;

output [
    "{",
    "\"holes\": ", show(holes),
    "}"
];