
% 2cc Hadamard Matrix Legendre Pairs for l=9

% Input data
int: l = 9;                     % odd length
int: m = (l - 1) div 2;         % number of quadratic constraints

% Decision variables: a[i], b[i] in {-1, +1}
array[1..l] of var {-1, 1}: a;
array[1..l] of var {-1, 1}: b;

% Linear constraints: sum of each sequence is 1
constraint sum(i in 1..l)(a[i]) = 1;
constraint sum(i in 1..l)(b[i]) = 1;

% Quadratic constraints: periodic autocorrelation sums
% For each shift s = 1..m: PAF(a, s) + PAF(b, s) = -2
constraint
  forall(s in 1..m) (
    sum(i in 1..l)(
      a[i] * a[((i + s - 1) mod l) + 1]
    ) +
    sum(i in 1..l)(
      b[i] * b[((i + s - 1) mod l) + 1]
    ) = -2
  );

solve satisfy;

% Output in JSON format with keys "a" and "b"
output [
  "{",
    "\"a\": [", join(",", [show(a[i]) | i in 1..l]), "],",
    "\"b\": [", join(",", [show(b[i]) | i in 1..l]), "]",
  "}"
];
