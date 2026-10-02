% Even Fibonacci numbers (Project Euler 2): each new term of the Fibonacci
% sequence is the sum of the previous two (1, 2, 3, 5, 8, 13, 21, ...). Find the
% sum of all even-valued terms that do not exceed four million. This problem has
% no instance data: the number of terms looked at and the limit are part of the
% problem statement.

int: n = 35;                  % terms f[1..n] are looked at; f[35] is the last one below 10 million
int: limit = 4000000;         % terms must stay below this

% f[i] = i-th term of the sequence, with f[1] = f[2] = 1
array[0..n] of var 0..10000000: f;
constraint f[0] = 0 /\ f[1] = 1 /\ f[2] = 1;
constraint forall(i in 3..n) (f[i] = f[i - 1] + f[i - 2]);

% x[i] = 1 if term i counts: it is even-valued and below the limit
array[0..n] of var bool: x;
constraint not x[0];
constraint forall(i in 1..n) (x[i] <-> (f[i] mod 2 = 0 /\ f[i] < limit));

% res = the sum of the counted terms
var 0..100000000: res;
constraint res = sum(i in 1..n) (bool2int(x[i]) * f[i]);

solve satisfy;

output ["{\"res\": ", show(res), "}"];
