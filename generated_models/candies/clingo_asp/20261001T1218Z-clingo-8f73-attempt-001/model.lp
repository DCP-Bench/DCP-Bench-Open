% Candies: a teacher gives every child in a line at least one candy; of two neighbours the one
% with the higher rating must get more candies. Use as few candies in total as possible.
% Instance facts: ratings(I, R): child I (numbered from 0 along the line) has rating R.
child(I) :- ratings(I,_).
children(N) :- N = #count { I : child(I) }.

% x(I, C): child I gets C candies, between 1 and the number of children (the bound used by the
% problem: a rating that rises along the whole line needs one more candy per child).
1 { x(I,1..N) } 1 :- child(I), children(N).

% Of two neighbours, the child with the higher rating gets more candies. Equal ratings do not
% constrain the candies.
:- ratings(I,R1), ratings(I + 1,R2), R1 > R2, x(I,C1), x(I + 1,C2), C1 <= C2.
:- ratings(I,R1), ratings(I + 1,R2), R1 < R2, x(I,C1), x(I + 1,C2), C1 >= C2.

% z is the total number of candies, which is to be minimised.
z(Z) :- Z = #sum { C,I : x(I,C) }.
#minimize { Z : z(Z) }.

#show x/2.
#show z/1.
