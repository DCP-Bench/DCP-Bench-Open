
% Include global constraints library
include "globals.mzn";

% Input data
int: n = 7;                         % number of items
array[1..n] of int: weights = [4, 3, 1, 3, 2, 5, 2];
int: num_bins = 5;                 % number of bins
int: capacity = 5;                 % capacity of each bin

% Decision variables
% bins[i] is the bin index (1..num_bins) to which item i is assigned
array[1..n] of var 1..num_bins: bins;

% Compute loads of each bin
% load[b] is the total weight in bin b
array[1..num_bins] of var 0..capacity: load;
constraint
  forall(b in 1..num_bins)(
    load[b] = sum(i in 1..n)(weights[i] * (bins[i] == b))
  );

% Capacity constraints: no bin exceeds its capacity
constraint
  forall(b in 1..num_bins)(
    load[b] <= capacity
  );

% Find any feasible assignment
solve satisfy;

% Output the bin assignment for each item as JSON
output [
  "{",
    "\"bins\": [" ++ join(",", [ show(bins[i]) | i in 1..n ]) ++ "]",
  "}"
];
