% Ages of the sons: three sons whose ages multiply to 36; knowing only their
% sum is not enough, so there is another triple with the same sum, and the
% oldest son is unique (the "blue eyes" clue).
% The puzzle is fixed by the problem; the instance carries no data.
% a1(V), a2(V), a3(V): the ages of the sons, oldest first. b1(V), b2(V), b3(V): the
% ages of the other triple with the same sum.
1 { a1(V) : V = 0..36 } 1.
1 { a2(V) : V = 0..36 } 1.
1 { a3(V) : V = 0..36 } 1.
1 { b1(V) : V = 0..36 } 1.
1 { b2(V) : V = 0..36 } 1.
1 { b3(V) : V = 0..36 } 1.

% Both triples have the product 36.
:- a1(X), a2(Y), a3(Z), X*Y*Z != 36.
:- b1(X), b2(Y), b3(Z), X*Y*Z != 36.

% The actual triple has a strictly oldest son (A1 > A2 >= A3), the other one may
% have twins first (B1 >= B2 >= B3).
:- a1(X), a2(Y), X <= Y.
:- a2(Y), a3(Z), Y < Z.
:- b1(X), b2(Y), X < Y.
:- b2(Y), b3(Z), Y < Z.

% The other triple has the same sum, and a different oldest son.
:- #sum { V,a1 : a1(V); V,a2 : a2(V); V,a3 : a3(V); -V,b1 : b1(V); -V,b2 : b2(V); -V,b3 : b3(V) } != 0.
:- a1(V), b1(V).

#show a1/1.
#show a2/1.
#show a3/1.
