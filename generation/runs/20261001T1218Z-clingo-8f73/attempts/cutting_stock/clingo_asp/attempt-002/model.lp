% Cutting stock: raw rolls are cut by a given set of cutting patterns, each pattern yielding a
% fixed number of pieces of every width. Decide how many times each pattern is used so that every
% width gets at least as many pieces as ordered, with as few raw rolls cut as possible.
% Instance facts: num_patterns(P), orders(W, O): pieces of width index W ordered,
% num_rolls_width(J, W, C): pattern J yields C pieces of width index W.
pattern(0..P-1) :- num_patterns(P).

% The most times a pattern is used. The problem allows 0 to 100. Below that, a cheapest cover never
% uses a pattern more often than the largest order: with more uses, one use less still gives
% every width it yields at least the largest order, so it is still a cover and costs a roll less.
max_order(M) :- M = #max { O : orders(_,O) }.
limit(M) :- max_order(M), M <= 100.
limit(100) :- max_order(M), M > 100.

% uses(J, V): pattern J is used at least V times. The number of uses is written in unary,
% so that the sums below are propagated tightly and the count of rolls is a plain count.
{ uses(J,V) } :- pattern(J), limit(L), V = 1..L.
:- uses(J,V), V > 1, not uses(J,V - 1).

% patterns_used(J, V): pattern J is used exactly V times.
patterns_used(J,0) :- pattern(J), not uses(J,1).
patterns_used(J,V) :- uses(J,V), not uses(J,V + 1).

% For each width, the pieces cut over all patterns meet the orders.
:- orders(W,O), #sum { C,J,V : uses(J,V), num_rolls_width(J,W,C) } < O.

% min_rolls_cut: the total number of raw rolls cut, which is to be minimised.
min_rolls_cut(S) :- S = #count { J,V : uses(J,V) }.
#minimize { 1,J,V : uses(J,V) }.

#show patterns_used/2.
#show min_rolls_cut/1.
