% Devil's word: put a plus or minus sign in front of every number of a list so
% that the signed numbers add up to the given total.
% arr(I, A): the I-th number is A; total(T) is the sum to reach.

% plus(I): the I-th number is added; otherwise it is subtracted.
{ plus(I) } :- arr(I,_).

% result(I, S): the I-th number with its chosen sign.
result(I,A) :- plus(I), arr(I,A).
result(I,-A) :- arr(I,A), not plus(I).

% The signed numbers add up to the total.
:- total(T), T != #sum { S,I : result(I,S) }.

#show result/2.
