% session2_subset_sum: a bank van had several bags of coins, each bag type holding a
% given number of coins. Thieves stole some bags, losing a given total number of
% coins. Find how many bags were stolen for each type of coin bag.
% Output: bags, a list with one count per bag type.

:- lib(ic).

model(Instance, Bags, [bags-Bags]) :-
    memberchk(coin_numbers-Coins, Instance),
    memberchk(total_coins_lost-Total, Instance),
    length(Coins, N),
    length(Bags, N),
    Bags :: 0..Total,

    % A total of the given number of coins were lost: the bags stolen of each
    % type, times the coins in that type of bag, add up to the total lost.
    ( foreach(B, Bags), foreach(C, Coins), foreach(P, Prods) do P #= B * C ),
    sum(Prods) #= Total.
