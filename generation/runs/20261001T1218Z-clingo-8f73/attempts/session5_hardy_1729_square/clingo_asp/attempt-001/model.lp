% Hardy-Ramanujan style puzzle: find four different numbers a, b, c, d between 1 and 100
% such that a^2 + b^2 = c^2 + d^2.
% The range 1..100 belongs to the problem statement (there is no instance data).

number(1..100).
1 { a(N) : number(N) } 1.
1 { b(N) : number(N) } 1.
1 { c(N) : number(N) } 1.
1 { d(N) : number(N) } 1.

% The four numbers are all different.
:- a(N), b(N).
:- a(N), c(N).
:- a(N), d(N).
:- b(N), c(N).
:- b(N), d(N).
:- c(N), d(N).

% The sum of squares of the first two equals the sum of squares of the other two. Each side is
% turned into one atom holding its value, so the comparison does not ground 100^4 combinations.
first_pair(A*A + B*B)  :- a(A), b(B).
second_pair(C*C + D*D) :- c(C), d(D).
:- first_pair(S), not second_pair(S).

#show a/1.
#show b/1.
#show c/1.
#show d/1.
