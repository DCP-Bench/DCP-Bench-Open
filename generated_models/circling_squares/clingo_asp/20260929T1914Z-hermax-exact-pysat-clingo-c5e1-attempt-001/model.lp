% Circling the squares: place a different number from 1 to 99 in each of ten
% squares of a circle so that the sum of the squares of any two adjacent numbers
% equals the sum of the squares of the two numbers opposite them. A, B, F and G
% are given.
% The puzzle is fixed by the problem; the instance carries no data.
square(a;b;c;d;e;f;g;h;i;k).

% v(S, V): the square S holds the number V.
1 { v(S,V) : V = 1..99 } 1 :- square(S).
% The numbers are all different.
:- v(S,V), v(T,V), S < T.

% The numbers that are given.
given(a,16). given(b,2). given(f,8). given(g,14).
:- given(S,V), not v(S,V).

% pairs(P, Q, R, S): the squares of the numbers in P and Q add up to the squares of
% the numbers in R and S.
pairs(a,b,f,g). pairs(b,c,g,h). pairs(c,d,h,i). pairs(d,e,i,k). pairs(e,f,k,a).
:- pairs(P,Q,R,S), #sum { V*V,P : v(P,V);  V*V,Q : v(Q,V);  -V*V,R : v(R,V);  -V*V,S : v(S,V) } != 0.

% The answer: one atom per square, a(V), b(V), ...
a(V) :- v(a,V).
b(V) :- v(b,V).
c(V) :- v(c,V).
d(V) :- v(d,V).
e(V) :- v(e,V).
f(V) :- v(f,V).
g(V) :- v(g,V).
h(V) :- v(h,V).
i(V) :- v(i,V).
k(V) :- v(k,V).
#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
#show f/1.
#show g/1.
#show h/1.
#show i/1.
#show k/1.
