% Fifty puzzle: each little dummy carries a number; knock over some of them so that the numbers
% on the dummies knocked over add up to exactly the target sum.
% Instance facts: target_sum(T), values(I, V): dummy I carries the number V.
dummy(I) :- values(I,_).

% knocked(I): dummy I is knocked over.
{ knocked(I) : dummy(I) }.

% The numbers on the knocked-over dummies add up to the target sum, neither more nor less.
:- target_sum(T), #sum { V,I : knocked(I), values(I,V) } != T.

% dummies(I, true/false): whether dummy I is knocked over.
dummies(I,true) :- knocked(I).
dummies(I,false) :- dummy(I), not knocked(I).

#show dummies/2.
