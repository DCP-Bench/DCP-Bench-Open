% Four numbers: given up to four distinct integers between 1 and 10, find three
% integers between 1 and 10 such that every given number is the sum of some
% subset of the three.
% numbers(I, N): the I-th given number is N. x(J, V): the J-th integer is V.
1 { x(J,V) : V = 1..10 } 1 :- J = 0..2.

% reach(I, J, S): the sum S can be made from a subset of the first J integers
% (the given numbers do not matter for this part, it only follows x).
reach(I,0,0) :- numbers(I,_).
reach(I,J+1,S) :- reach(I,J,S), J = 0..2.
reach(I,J+1,S+V) :- reach(I,J,S), x(J,V).

% Every given number is the sum of a subset of the three integers.
:- numbers(I,N), not reach(I,3,N).

#show x/2.
