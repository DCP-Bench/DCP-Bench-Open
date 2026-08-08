include "globals.mzn";

% The total weight is 40 pounds, split into 4 integer pieces
int: total_weight = 40;
int: num_pieces = 4;

% Decision variables: weights of the four pieces, in ascending order
array[1..num_pieces] of var 1..total_weight: weights;

% Constraint: sum of weights is 40
constraint sum(weights) == total_weight;

% Enforce ascending order to avoid symmetric solutions
constraint forall(i in 1..num_pieces-1) (
    weights[i] <= weights[i+1]
);

% We want to check that every integral weight from 1 to 40 can be weighed
% using the four pieces on a balance scale.
% Each piece can be on the left pan (-1), right pan (+1), or not used (0).
% For each weight w in 1..40, there must exist a combination of placements
% such that sum of (placement[i] * weights[i]) == w.

% Define the domain for placements: -1, 0, 1 for each piece and each weight
array[1..total_weight, 1..num_pieces] of var -1..1: placements;

% For each weight w, the sum of placements * weights must be equal to w
constraint forall(w in 1..total_weight) (
    sum(i in 1..num_pieces)(placements[w,i] * weights[i]) == w
);

% Solve for any solution satisfying the constraints
solve satisfy;

output [
    "{",
    "\"weights\": ", show(weights),
    "}"
];