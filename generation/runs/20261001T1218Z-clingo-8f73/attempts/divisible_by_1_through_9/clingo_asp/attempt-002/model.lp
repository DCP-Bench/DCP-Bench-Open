% Divisible by 1 through 9: find a 10-digit number that uses each of the digits 0 to 9 exactly
% once and where the number formed by the first n digits is divisible by n, for n = 1 to 10.
% The digits and the divisors belong to the problem statement (there is no instance data).
%
% Probe, not a solution: clingo integers are 32 bits (at most 2147483647), so the 10-digit number
% cannot be written. This program reports the number formed by the first nine digits, which fits,
% to show that the digit search itself works and only the last step is out of range.

position(0..9).

% digit(P, D): the digit at position P (counted from the left, starting at 0) is D.
1 { digit(P,D) : D = 0..9 } 1 :- position(P).

% Every digit is used exactly once.
:- D = 0..9, #count { P : digit(P,D) } != 1.

% prefix(N, V): the number formed by the first N digits is V and is divisible by N. It is built
% one digit at a time, and a prefix that is not divisible by its length is never derived, which
% keeps the grounding small. The tenth digit is a 0, as divisibility by 10 requires.
prefix(1,D) :- digit(0,D).
prefix(N + 1,V) :- prefix(N,W), digit(N,D), N < 9, V = 10 * W + D, V \ (N + 1) = 0.
:- not prefix(9,_).
:- not digit(9,0).

number(V) :- prefix(9,V).

#show number/1.
