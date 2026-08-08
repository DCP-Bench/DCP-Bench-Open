include "globals.mzn";

% We want to find integers a, b, n, p such that:
% 1) a - b = p, where p is prime
% 2) a * b = n^2 (a perfect square)
% 3) a >= 2012
% 4) a, b, n, p > 0

% We will search for a in a reasonable range starting from 2012.
% To keep the model finite, we set an upper bound for a.
% Since the problem asks for the smallest a >= 2012, we will minimize a.

int: a_min = 2012;
int: a_max = 10000; % upper bound for search, can be increased if needed
int: p_max = a_max; % upper bound for prime p

% Decision variables
var a_min..a_max: a;
var 1..a_max: b;
var 1..a_max: n;
var 2..p_max: p; % p is prime and positive difference

% Constraint: a - b = p
constraint a - b = p;

% Constraint: a * b = n^2 (perfect square)
constraint a * b = n * n;

% Constraint: p is prime
% We define a predicate to check primality
predicate is_prime(int: x) =
  x > 1 /\
  forall(i in 2..int(sqrt(float(x)))) (
    x mod i != 0
  );

constraint is_prime(p);

% Constraint: a >= 2012 (already ensured by domain)

% Additional constraints to ensure b > 0 and b < a (since p = a - b > 0)
constraint b > 0 /\ b < a;

solve minimize a;

output [
    "{",
    "\"a\": ", show(a), ",",
    "\"b\": ", show(b), ",",
    "\"n\": ", show(n), ",",
    "\"p\": ", show(p),
    "}"
];