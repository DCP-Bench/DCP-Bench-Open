include "globals.mzn";

% Input data
int: num_items = 7;
array[1..num_items] of int: weights = [4, 3, 1, 3, 2, 5, 2];
int: capacity = 5;
int: num_bins = 5;

% Decision variables
% bins[i] is the bin assigned to item i (1..num_bins)
array[1..num_items] of var 1..num_bins: bins;

% Constraints
% For each bin, sum of weights of items assigned to it <= capacity
constraint
  forall(b in 1..num_bins) (
    sum(i in 1..num_items where bins[i] == b) (weights[i]) <= capacity
  );

solve satisfy;

output [
  "{",
  "\"bins\": ", show(bins),
  "}"
];