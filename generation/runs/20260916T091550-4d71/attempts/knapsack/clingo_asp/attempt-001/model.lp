% Knapsack: pick items to maximize total value without exceeding the pack's
% weight capacity.
item(I) :- values(I,_).

% Each item is either taken or not.
{ x(I,1) } :- item(I).
x(I,0) :- item(I), not x(I,1).

% The weight carried stays within the capacity.
:- capacity(C), #sum { W,I : x(I,1), weights(I,W) } > C.

#maximize { V,I : x(I,1), values(I,V) }.
#show x/2.
