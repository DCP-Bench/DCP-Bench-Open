include "globals.mzn";

% Input data
int: l = 9; % must be an odd positive integer
int: m = (l - 1) div 2;

% Domains: variables take values in {-1, 1}
set of int: D = {-1, 1};

% Decision variables
array[1..l] of var D: a;
array[1..l] of var D: b;

% Function to compute periodic autocorrelation function PAF for sequence x at shift s
function var int: PAF(array[int] of var int: x, int: s) =
    sum(i in 1..l)(x[i] * x[if i + s <= l then i + s else i + s - l endif]);

% Constraints
constraint
    % m quadratic constraints: PAF(A,s) + PAF(B,s) = -2 for s=1..m
    forall(s in 1..m) (
        PAF(a, s) + PAF(b, s) = -2
    )
    /\
    % 2 linear constraints: sum of a_i = 1 and sum of b_i = 1
    sum(i in 1..l)(a[i]) = 1 /\
    sum(i in 1..l)(b[i]) = 1;

solve satisfy;

output [
    "{",
    "\"a\": ", show(a), ",",
    "\"b\": ", show(b),
    "}"
];