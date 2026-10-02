% Cutting stock: raw rolls are cut by a given set of cutting patterns, each pattern yielding a
% fixed number of pieces of every width. Decide how many times each pattern is used so that every
% width gets at least as many pieces as ordered, with as few raw rolls cut as possible.
% Instance facts: num_patterns(P), orders(W, O): pieces of width index W ordered,
% num_rolls_width(J, W, C): pattern J yields C pieces of width index W.
pattern(0..P-1) :- num_patterns(P).
width(W) :- orders(W,_).

% patterns_used(J, V): pattern J is used V times. The count of any pattern is between 0 and 100,
% the bound the problem itself declares.
1 { patterns_used(J,V) : V = 0..100 } 1 :- pattern(J).

% For each width, the pieces cut over all patterns meet the orders.
:- orders(W,O), #sum { V*C,J : patterns_used(J,V), num_rolls_width(J,W,C) } < O.

% min_rolls_cut: the total number of raw rolls cut, which is to be minimised.
min_rolls_cut(S) :- S = #sum { V,J : patterns_used(J,V) }.
#minimize { S : min_rolls_cut(S) }.

#show patterns_used/2.
#show min_rolls_cut/1.
