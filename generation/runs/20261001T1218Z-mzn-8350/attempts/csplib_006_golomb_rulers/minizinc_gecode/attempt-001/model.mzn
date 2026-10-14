% Golomb ruler: place `size` marks at integer positions on a ruler, the first at
% 0, so that all differences between two marks are distinct, with the ruler (the
% position of the last mark) as short as possible.
include "globals.mzn";

int: size;  % number of marks on the ruler

% marks[i] = position of the i-th mark. The upper bound size * size is the
% reference's own bound on the length.
array[1..size] of var 0..size * size: marks;

% the first mark is at 0
constraint marks[1] = 0;

% marks are in increasing order
constraint forall(i in 1..size - 1) (marks[i] < marks[i + 1]);

% Golomb condition: the differences between all pairs of marks are distinct
constraint alldifferent([marks[j] - marks[i] | i in 1..size - 1, j in i + 1..size]);

% Implied: the differences between marks that are k places apart are k distinct
% positive integers (the k consecutive gaps), so they add up to at least
% 1 + 2 + ... + k. This follows from the constraints above and removes no solution;
% it gives Gecode a lower bound on every mark from the start.
constraint forall(i in 1..size - 1, j in i + 1..size) (marks[j] - marks[i] >= (j - i) * (j - i + 1) div 2);

% the length of the ruler is the position of its last mark, to be minimised
var int: ruler_length = marks[size];
var int: objective = ruler_length;
solve minimize objective;

output ["{\"marks\": [", join(", ", [show(marks[i]) | i in 1..size]), "], \"length\": ", show(ruler_length), "}"];
