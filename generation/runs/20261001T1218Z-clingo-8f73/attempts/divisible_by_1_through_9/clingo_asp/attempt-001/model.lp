% Divisible by 1 through 9: find a 10-digit number that uses each of the digits 0 to 9 exactly
% once and where the number formed by the first n digits is divisible by n, for n = 1 to 10.
% The digits and the divisors belong to the problem statement (there is no instance data).

position(0..9).

% digit(P, D): the digit at position P (counted from the left, starting at 0) is D.
1 { digit(P,D) : D = 0..9 } 1 :- position(P).

% Every digit is used exactly once.
:- D = 0..9, #count { P : digit(P,D) } != 1.

% prefix(N, V): the number formed by the first N digits is V and is divisible by N. It is built
% one digit at a time, and a prefix that is not divisible by its length is never derived, which
% keeps the grounding small.
prefix(1,D) :- digit(0,D).
prefix(N + 1,V) :- prefix(N,W), digit(N,D), N < 10, V = 10 * W + D, V \ (N + 1) = 0.

% All ten prefixes must exist, that is, all of them are divisible.
:- not prefix(10,_).

number(V) :- prefix(10,V).

#show number/1.
