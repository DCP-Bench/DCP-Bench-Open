% Abbot's puzzle: 100 bushels of corn are shared among 100 people. Each man gets three bushels,
% each woman two and each child half a bushel, and there are five times as many women as men.
% Find the number of men, women and children.
% This problem has no instance data: every number below belongs to the problem statement.

% Each group has between 0 and 100 people (the reference's domain).
1 { men(V)      : V = 0..100 } 1.
1 { women(V)    : V = 0..100 } 1.
1 { children(V) : V = 0..100 } 1.

% There are 100 people in total. The letters m, w and c keep the three terms apart, since
% an aggregate merges terms with the same tuple.
:- #sum { V,m : men(V) ; V,w : women(V) ; V,c : children(V) } != 100.

% The corn handed out is 100 bushels. In half bushels, a man gets 6, a woman 4 and a child 1, so
% the total is 200 half bushels.
:- #sum { 6*V,m : men(V) ; 4*V,w : women(V) ; V,c : children(V) } != 200.

% There are five times as many women as men.
:- men(M), women(W), W != 5*M.

#show men/1.
#show women/1.
#show children/1.
