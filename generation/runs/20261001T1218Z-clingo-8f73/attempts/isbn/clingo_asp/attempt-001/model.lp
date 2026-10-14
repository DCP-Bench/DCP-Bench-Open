% ISBN-13: some digits of a 13-digit ISBN are unknown; find them so that the number is a valid
% ISBN-13: it starts with 978 or 979 and the last digit is the check digit of the first 12.
% Instance facts: isbn_init(I, V): the I-th digit (from 0) is V, or -1 when it is unknown.
position(I) :- isbn_init(I,_).
len(N) :- N = #count { I : position(I) }.

% isbn(I, D): the I-th digit of the ISBN is D, a digit between 0 and 9.
1 { isbn(I,D) : D = 0..9 } 1 :- position(I).

% The digits that are known keep their value (-1 marks an unknown digit).
:- isbn_init(I,V), V != -1, not isbn(I,V).

% An ISBN-13 starts with 978 or 979.
:- not isbn(0,9).
:- not isbn(1,7).
:- not isbn(2,8), not isbn(2,9).

% weight(I, W): the first 12 digits are multiplied alternately by 1 and 3, starting with 1.
weight(I,1) :- position(I), I \ 2 == 0.
weight(I,3) :- position(I), I \ 2 == 1.

% The check digit (the last one) is (10 - (sum mod 10)) mod 10, where sum is the sum of the
% weighted first 12 digits.
check_sum(S) :- S = #sum { D * W,I : isbn(I,D), weight(I,W), len(N), I < N - 1 }.
:- check_sum(S), len(N), not isbn(N - 1,(10 - S \ 10) \ 10).

#show isbn/2.
