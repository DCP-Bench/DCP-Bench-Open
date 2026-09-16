% Subset sum: how many bags of each coin type were stolen, given the total
% number of coins lost.
index(I) :- coin_numbers(I,_).

% Bound each coin type by the most bags its own value could ever reach. Letting
% every count run to the full total grounds hundreds of useless atoms per type
% and the search never finishes.
allowed(I,0..M) :- coin_numbers(I,C), total_coins_lost(T), M = T/C.

1 { bags(I,K) : allowed(I,K) } 1 :- index(I).

lost(S) :- S = #sum { C*K,I : bags(I,K), coin_numbers(I,C) }.
:- lost(S), total_coins_lost(T), S != T.

#show bags/2.
