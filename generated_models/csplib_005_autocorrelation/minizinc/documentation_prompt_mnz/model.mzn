include "globals.mzn";

% Input data
int: n = 10;

% Decision Variables
% sequence[i] in {-1, 1}
array[0..n-1] of var -1..1: sequence;

% Constraint: sequence elements must be either -1 or 1
constraint forall(i in 0..n-1) (
    sequence[i] = -1 \/ sequence[i] = 1
);

% Compute autocorrelations C_k for k = 1..n-1 with periodic boundary conditions
array[1..n-1] of var int: C;
constraint forall(k in 1..n-1) (
    C[k] = sum(i in 0..n-1)(sequence[i] * sequence[(i + k) mod n])
);

% Energy E = sum of squares of autocorrelations
var int: E = sum(k in 1..n-1)(C[k] * C[k]);

% Objective: minimize energy E
solve minimize E;

output [
    "{",
    "\"sequence\": ", show(sequence), ",",
    "\"E\": ", show(E),
    "}"
];