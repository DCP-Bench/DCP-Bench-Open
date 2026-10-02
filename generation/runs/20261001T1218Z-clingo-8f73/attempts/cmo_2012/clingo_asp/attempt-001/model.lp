% CMO 2012 number puzzle: find positive integers a and b, with a at least min_a, such that
% a - b is a prime number p and a * b is a perfect square n * n; a is to be as small as possible.
% Instance facts: min_a(L): the lower bound for a; max_val(M): the upper bound for a and b (and
% n); primes are the primes below max_val.

% Primes below max_val by a sieve: composite(C) holds for every product of two numbers >= 2.
composite(X * Y) :- max_val(M), X = 2..M, Y = 2..M / X.
prime(P) :- max_val(M), P = 2..M - 1, not composite(P).

% A solution is a triple (n, b, a) with a * b = n * n, listed with its a. Instead of choosing
% a, b and n separately, which would force the grounder to pair every a with every b (around
% 10^8 pairs for max_val = 10000), only the pairs (n, b) with b <= n <= max_val are walked.
% Given them, a is n * n / b, which has to divide exactly (a * b = n * n), lie between min_a
% and max_val, and a - b has to be prime. The start of the range for b is where a stops
% exceeding max_val; b <= n holds because a >= b is required and a * b = n * n.
triple(N,B,A) :- min_a(L), max_val(M), N = 1..M, B = (N * N + M - 1) / M..N,
                 A = N * N / B, A * B == N * N, A >= L, A <= M, prime(A - B).

% Exactly one triple is chosen; its values are the answer.
1 { pick(N,B,A) : triple(N,B,A) } 1.
a(A) :- pick(_,_,A).
b(B) :- pick(_,B,_).
n(N) :- pick(N,_,_).
p(A - B) :- pick(_,B,A).

% The smallest value of a is wanted.
#minimize { A : a(A) }.

#show a/1.
#show b/1.
#show n/1.
#show p/1.
