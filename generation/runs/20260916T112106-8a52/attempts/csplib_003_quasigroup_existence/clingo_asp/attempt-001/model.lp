% Quasigroup existence, QG3: a Latin square in which (a*b)*(b*a) = a for every
% pair of elements.
element(0..M-1) :- m(M).

1 { quasigroup(I,J,V) : element(V) } 1 :- element(I), element(J).

% Each element occurs once in every row and once in every column.
:- quasigroup(I,J,V), quasigroup(I,K,V), J < K.
:- quasigroup(I,J,V), quasigroup(K,J,V), I < K.

% The QG3 property, read straight off the table rather than through an index
% variable: the entry at (a*b, b*a) must be a.
:- quasigroup(A,B,AB), quasigroup(B,A,BA), quasigroup(AB,BA,V), V != A.

#show quasigroup/3.
