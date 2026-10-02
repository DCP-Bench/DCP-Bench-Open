% KenKen: fill an n by n grid with the digits 1 to n so that every row and every column has each
% digit once, and every cage (a group of cells) reaches its target number with its digits, which
% may repeat inside a cage. A cage of two cells reaches the target by their sum, product,
% difference or quotient; a cage of any other size reaches it by the sum or the product of its digits.
% Instance facts: n(N), problem(I, 0, Target): the target of cage I,
% problem(I, 1, K, 0, R) and problem(I, 1, K, 1, C): the K-th cell of cage I is in row R and
% column C, counted from 1.
digit(1..N) :- n(N).
index(0..N-1) :- n(N).

% x(R, C, V): the cell in row R and column C (counted from 0) holds the digit V. Every
% cell holds one digit, and each row and each column holds every digit once.
1 { x(R,C,V) : digit(V) } 1 :- index(R), index(C).
1 { x(R,C,V) : index(C) } 1 :- index(R), digit(V).
1 { x(R,C,V) : index(R) } 1 :- index(C), digit(V).

% target(I, T): cage I has target T, and size(I, S): it has S cells.
target(I,T) :- problem(I,0,T).
size(I,S) :- target(I,_), S = #count { K : problem(I,1,K,0,_) }.

% val(I, K, V): the K-th cell of cage I holds the digit V (the cells in the instance are counted from 1).
val(I,K,V) :- problem(I,1,K,0,R), problem(I,1,K,1,C), x(R - 1,C - 1,V).

% total(I, S): the digits of cage I add up to S.
total(I,S) :- target(I,_), S = #sum { V,K : val(I,K,V) }.

% product(I, K, P): the first K+1 digits of cage I multiply to P, so the last one is the
% product of the whole cage (the aggregates of clingo have no product).
product(I,0,V) :- val(I,0,V).
product(I,K + 1,P * V) :- product(I,K,P), val(I,K + 1,V).
cage_product(I,P) :- size(I,S), product(I,S - 1,P).

% A cage of two cells reaches its target by sum, product, difference or quotient of the digits A and B
% (in either order).
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), A + B == T.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), A * B == T.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), A - B == T.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), B - A == T.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), A * T == B.
reached(I) :- size(I,2), target(I,T), val(I,0,A), val(I,1,B), B * T == A.

% A cage of any other size reaches its target by the sum or the product of its digits.
reached(I) :- size(I,S), S != 2, target(I,T), total(I,T).
reached(I) :- size(I,S), S != 2, target(I,T), cage_product(I,T).

% Every cage reaches its target.
:- target(I,_), not reached(I).

#show x/3.
