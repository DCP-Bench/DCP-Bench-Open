% Added corners: digits 1..8 around a ring, each square the sum of its two
% adjoining circles. The puzzle fixes its own size, so there are no parameters.
include "globals.mzn";

int: n = 8;
array[1..n] of var 1..n: positions;

constraint all_different(positions);

% Reading order: a b c / d _ e / f g h. Each of b, d, e and g is a square
% flanked by two circles.
constraint positions[2] = positions[1] + positions[3];
constraint positions[4] = positions[1] + positions[6];
constraint positions[5] = positions[3] + positions[8];
constraint positions[7] = positions[6] + positions[8];

solve satisfy;

output ["{\"positions\": [", join(", ", [show(positions[i]) | i in 1..n]), "]}"];
