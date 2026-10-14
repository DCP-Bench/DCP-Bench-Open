% Hanging weights: thirteen weights A-M, each an integer from 1 to 13 and all
% different, hang from a system of bars that has to balance.
% The puzzle is fixed by the problem; the instance carries no data.
object(a;b;c;d;e;f;g;h;i;j;k;l;m).

% Every weight is one value from 1 to 13, and no value is used twice.
1 { w(O,V) : V = 1..13 } 1 :- object(O).
:- w(O1,V), w(O2,V), O1 < O2.

% Every bar balances: the weights on either side of the pivot, each times its
% distance from the pivot, are equal, and a bar hanging beneath another counts as
% one weight equal to its total. The bottom right bar has 5*C = D and the bar
% above it 3*G = 2*(C+D). balance(N, O, C) puts the term C*O into balance N; the
% terms of one balance, left side minus right side, add up to zero.
balance(1,a,4). balance(1,b,-1).
balance(2,c,5). balance(2,d,-1).
balance(3,e,3). balance(3,f,-2).
balance(4,g,3). balance(4,c,-2). balance(4,d,-2).
balance(5,a,3). balance(5,b,3). balance(5,j,2). balance(5,k,-1). balance(5,g,-2). balance(5,c,-2). balance(5,d,-2).
balance(6,h,3). balance(6,e,-2). balance(6,f,-2). balance(6,i,-3).
balance(7,h,1). balance(7,i,1). balance(7,e,1). balance(7,f,1). balance(7,l,-1). balance(7,m,-4).
balance(8,l,4). balance(8,m,4). balance(8,h,4). balance(8,i,4). balance(8,e,4). balance(8,f,4).
balance(8,j,-3). balance(8,k,-3). balance(8,g,-3). balance(8,a,-3). balance(8,b,-3). balance(8,c,-3). balance(8,d,-3).
:- balance(N,_,_), #sum { C*V,O : balance(N,O,C), w(O,V) } != 0.

% The answer: one atom per weight, a(V), b(V), ...
a(V) :- w(a,V).
b(V) :- w(b,V).
c(V) :- w(c,V).
d(V) :- w(d,V).
e(V) :- w(e,V).
f(V) :- w(f,V).
g(V) :- w(g,V).
h(V) :- w(h,V).
i(V) :- w(i,V).
j(V) :- w(j,V).
k(V) :- w(k,V).
l(V) :- w(l,V).
m(V) :- w(m,V).
#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
#show f/1.
#show g/1.
#show h/1.
#show i/1.
#show j/1.
#show k/1.
#show l/1.
#show m/1.
