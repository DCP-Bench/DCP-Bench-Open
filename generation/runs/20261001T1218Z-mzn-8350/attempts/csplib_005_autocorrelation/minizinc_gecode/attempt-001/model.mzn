% Low autocorrelation binary sequences: choose a sequence of n values, each +1
% or -1, that minimises the sum of the squared periodic (cyclic) autocorrelations.
include "globals.mzn";

int: n;  % length of the sequence

% sequence[i] = the i-th bit of the sequence, either -1 or +1 (0 is excluded)
array[0..n - 1] of var {-1, 1}: sequence;

% paf[s] = periodic autocorrelation at shift s: the sum over all positions of
% the bit times the bit s places further on, wrapping around at the end
array[1..n - 1] of var -n..n: paf;
constraint forall(s in 1..n - 1) (paf[s] = sum(i in 0..n - 1) (sequence[i] * sequence[(i + s) mod n]));

% the energy to be minimised: the sum of the squares of the autocorrelations
var int: energy = sum(s in 1..n - 1) (paf[s] * paf[s]);
var int: objective = energy;
solve minimize objective;

output ["{\"sequence\": [", join(", ", [show(sequence[i]) | i in 0..n - 1]), "]}"];
