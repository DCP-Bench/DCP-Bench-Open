% CMO 2012: the smallest a at or above a minimum such that a - b is prime and
% a * b is a perfect square.
int: min_a;
int: max_val;

var min_a..max_val: a;
var 1..max_val: b;
var 0..max_val: n;
var 2..max_val: p;

constraint a >= b;
constraint p = a - b;
constraint a * b = n * n;

% p is prime: any composite below max_val has a factor no larger than its own
% square root, so testing divisors up to that bound is enough.
constraint forall(d in 2..ceil(sqrt(int2float(max_val)))) (
    p mod d != 0 \/ p = d
);

var int: objective = a;
solve minimize objective;

output ["{\"a\": ", show(a), ", \"b\": ", show(b),
        ", \"n\": ", show(n), ", \"p\": ", show(p), "}"];
