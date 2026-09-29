% De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of `base`
% symbols, of length base^n, in which every string of n symbols occurs exactly
% once. Modelled as a cycle through all base^n windows of n consecutive symbols.
include "globals.mzn";

int: base;  % size of the alphabet
int: n;     % order: length of the strings that must all appear
int: m = pow(base, n);  % length of the sequence = number of distinct strings

% x[i] = the number (in the given base) read from the window starting at position i
array[1..m] of var 0..m - 1: x;
% binary[i, j] = j-th symbol (most significant first) of the window starting at position i
array[1..m, 1..n] of var 0..base - 1: binary;

% every possible string occurs exactly once, i.e. all window numbers differ
constraint all_different(x);

% link each window number to its symbols
constraint forall(i in 1..m) (x[i] = sum(j in 1..n) (binary[i, j] * pow(base, n - j)));

% consecutive windows overlap: window i shifted by one symbol is window i-1 ...
constraint forall(i in 2..m, j in 2..n) (binary[i - 1, j] = binary[i, j - 1]);
% ... and the last window continues into the first one, closing the cycle
constraint forall(j in 2..n) (binary[m, j] = binary[1, j - 1]);

% the sequence is the first symbol of every window
array[1..m] of var 0..base - 1: de_bruijn;
constraint forall(i in 1..m) (de_bruijn[i] = binary[i, 1]);

solve satisfy;

output ["{\"de_bruijn\": [", join(", ", [show(de_bruijn[i]) | i in 1..m]), "]}"];
