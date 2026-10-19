% cmo_2012: given two positive integers a and b, where a - b is a prime number and
% a * b is a perfect square n^2, find the smallest a no less than min_a (b > 0).
% Outputs a, b, n, p, where p = a - b.

:- lib(ic).

% Primes up to the instance bound max_val, by trial division.
is_prime(N) :- N >= 2, \+ has_divisor(N, 2).

has_divisor(N, D) :-
    D * D =< N,
    (   N mod D =:= 0
    ->  true
    ;   D1 is D + 1,
        has_divisor(N, D1)
    ).

primes_from(I, Max, Ps) :-
    I > Max, !,
    Ps = [].
primes_from(I, Max, Ps) :-
    (   is_prime(I)
    ->  Ps = [I | Rest]
    ;   Ps = Rest
    ),
    I1 is I + 1,
    primes_from(I1, Max, Rest).

model(Instance, [A, P, N], [a-A, b-B, n-N, p-P], min(A)) :-
    memberchk(min_a-MinA, Instance),
    memberchk(max_val-MaxVal, Instance),
    primes_from(2, MaxVal, Primes),

    % a is at least min_a, and a is at most max_val
    A :: MinA..MaxVal,

    % a - b is a prime number: p is prime and b = a - p
    P :: Primes,
    B :: 1..MaxVal,
    B #= A - P,

    % b should be larger than 0
    B #>= 1,

    % a * b is a perfect square n^2, with n a positive integer
    N :: 1..MaxVal,
    A * B #= N * N.

% Label a first (smallest value first), then p, then n.
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).
