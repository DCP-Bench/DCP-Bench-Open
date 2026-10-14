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

% Implied (both follow from the definition and remove no sequence):
% - the n products in paf[s] are +1 or -1 and the number of -1 among them is
%   even (the products along each cycle of the shift multiply to 1), so
%   paf[s] = n - 4 * q for a whole number q; q is stated as a variable so that
%   Gecode works with the few values paf[s] can take
% - shifting by s or by n - s gives the same autocorrelation
array[1..n - 1] of var 0..n div 2: q;
constraint forall(s in 1..n - 1) (paf[s] = n - 4 * q[s]);
constraint forall(s in 1..n - 1) (paf[s] = paf[n - s]);

% the energy to be minimised: the sum of the squares of the autocorrelations
var int: energy = sum(s in 1..n - 1) (paf[s] * paf[s]);
var int: objective = energy;
solve minimize objective;

output ["{\"sequence\": [", join(", ", [show(sequence[i]) | i in 0..n - 1]), "]}"];
