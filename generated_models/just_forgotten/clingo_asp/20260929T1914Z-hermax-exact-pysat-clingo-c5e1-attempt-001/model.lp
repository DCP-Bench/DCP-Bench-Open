% Just forgotten: Joe's account number uses each digit 0 to n-1 once. In each of
% several tried sets exactly some given number of digits are in the right place.
% sets(S, I, D): the S-th tried set has the digit D at position I.
% num_correct_digits(K): digits in the right place in each set.
position(I) :- sets(_,I,_).

% x(I, D): the account number has the digit D at position I. The digits are 0 to n-1,
% the same numbers as the positions.
1 { x(I,D) : position(D) } 1 :- position(I).

% Each digit is used exactly once.
:- x(I1,D), x(I2,D), I1 < I2.

% Every tried set has exactly K digits in the position they have in the number.
:- sets(S,_,_), num_correct_digits(K), K != #count { I : sets(S,I,D), x(I,D) }.

#show x/2.
