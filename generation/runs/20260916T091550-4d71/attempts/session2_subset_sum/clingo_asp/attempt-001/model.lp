% Subset sum: how many bags of each coin type were stolen, given the total
% number of coins lost.
index(I) :- coin_numbers(I,_).
% No single coin type can contribute more bags than the total it would reach.
count(0..T) :- total_coins_lost(T).

1 { bags(I,K) : count(K) } 1 :- index(I).

lost(S) :- S = #sum { C*K,I : bags(I,K), coin_numbers(I,C) }.
:- lost(S), total_coins_lost(T), S != T.

#show bags/2.
