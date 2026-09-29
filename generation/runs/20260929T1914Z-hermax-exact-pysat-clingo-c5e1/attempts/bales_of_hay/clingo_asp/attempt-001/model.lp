% Bales of hay: the bales were weighed in all combinations of two and the
% weights, in numerical order, are given. Find the weight of each bale.
% n(N): number of bales. weights(K, W): the K-th written-down weight is W.
% bales(I, V): bale I weighs V.
1 { bales(I,V) : V = 0..50 } 1 :- n(N), I = 0..N-1.

% pair(I, J, S): the two bales I < J weigh S together.
pair(I,J,VI+VJ) :- bales(I,VI), bales(J,VJ), I < J.

% The written-down weights are exactly the weights of the pairs: every pair weighs
% one of them, and each weight value is the weight of as many pairs as times it was
% written down.
:- pair(I,J,S), not weights(_,S).
:- weights(_,W), #count { K : weights(K,W) } != #count { I,J : pair(I,J,W) }.

#show bales/2.
