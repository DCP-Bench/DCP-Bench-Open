% Calvin puzzle: fill an n x n grid with the numbers 1 to n*n so that each number is placed
% exactly three squares from the previous one when moving along a row or column, or exactly two
% squares from it when moving diagonally.
% Instance facts: n(N).
cell(0..N-1,0..N-1) :- n(N).
number(1..N*N) :- n(N).

% jump(I,J,A,B): a move from square (I,J) to square (A,B) that stays in the grid is allowed.
% Type I: vertically or horizontally, exactly three squares away. Type II: diagonally, exactly two squares away.
jump(I,J,A,B) :- cell(I,J), cell(A,B), |A-I| == 3, B == J.
jump(I,J,A,B) :- cell(I,J), cell(A,B), |B-J| == 3, A == I.
jump(I,J,A,B) :- cell(I,J), cell(A,B), |A-I| == 2, |B-J| == 2.

% at(K,I,J): the number K is in square (I,J). Every number is in exactly one square and every
% square holds exactly one number (all numbers are different).
1 { at(K,I,J) : cell(I,J) } 1 :- number(K).
1 { at(K,I,J) : number(K) } 1 :- cell(I,J).

% The next number is placed with a valid move from the previous one.
:- at(K,I,J), number(K+1), not 1 { at(K+1,A,B) : jump(I,J,A,B) }.

% x(I,J,K): square (I,J) holds the number K.
x(I,J,K) :- at(K,I,J).

#show x/3.
