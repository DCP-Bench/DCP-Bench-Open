% Dudeney numbers: a positive integer that is a perfect cube whose digits add up
% to its cube root. Find one larger than 1, with at most n digits.
% n(N): most digits of the number.
% root(R): the cube root, at least 1 and, the digits being at most 9 each, at most 9n.
1 { root(R) : R = 1..9*N } 1 :- n(N).

% The number is the cube of the root, larger than 1, and has at most n digits.
:- root(1).
:- root(R), n(N), R*R*R >= 10**N.

% The digits of the cube add up to the root: the digit at place K of R*R*R is
% (R*R*R / 10**K) modulo 10.
:- root(R), n(N), #sum { (R*R*R / 10**K) \ 10, K : K = 0..N-1 } != R.

number(R*R*R) :- root(R).
#show number/1.
