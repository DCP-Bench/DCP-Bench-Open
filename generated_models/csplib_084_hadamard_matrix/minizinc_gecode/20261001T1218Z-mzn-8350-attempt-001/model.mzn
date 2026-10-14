% Hadamard matrix Legendre pairs: for an odd l, find two sequences a and b of
% length l with entries +1 or -1, each summing to 1, such that for every shift s
% from 1 to (l - 1) / 2 the periodic autocorrelations of a and b add up to -2.
include "globals.mzn";

int: l;  % sequence length, an odd positive integer

int: m = (l - 1) div 2;  % number of shifts that are constrained

% a[i] and b[i] are the i-th entries of the two sequences (either -1 or +1; 0 is excluded)
array[0..l - 1] of var {-1, 1}: a;
array[0..l - 1] of var {-1, 1}: b;

% each sequence has the entries summing to 1
constraint sum(a) = 1;
constraint sum(b) = 1;

% for every shift s the two periodic autocorrelations (the sum over positions of
% an entry times the entry s places further on, wrapping around) add up to -2
constraint forall(s in 1..m)
    (sum(i in 0..l - 1) (a[i] * a[(i + s) mod l]) + sum(i in 0..l - 1) (b[i] * b[(i + s) mod l]) = -2);

solve satisfy;

output ["{\"a\": [", join(", ", [show(a[i]) | i in 0..l - 1]), "], \"b\": [", join(", ", [show(b[i]) | i in 0..l - 1]), "]}"];
