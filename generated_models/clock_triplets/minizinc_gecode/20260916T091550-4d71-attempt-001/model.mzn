% Clock triplets: rearrange 1..12 around a clock face so that no three adjacent
% numbers sum above 21. The puzzle fixes the clock, so there are no parameters.
include "globals.mzn";

int: n = 12;
array[1..n] of var 1..n: x;
% The reference caps the largest triplet sum at 21 by declaring the variable's
% domain rather than by optimizing.
var 0..21: triplet_sum;

constraint all_different(x);

% Triplets wrap around the face.
constraint forall(i in 1..n) (
    x[i] + x[(i + n - 2) mod n + 1] + x[(i + n - 3) mod n + 1] <= triplet_sum
);

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 1..n]), "]}"];
