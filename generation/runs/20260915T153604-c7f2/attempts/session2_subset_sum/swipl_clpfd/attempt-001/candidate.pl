:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Subset sum: how many bags of each coin type were stolen, given the total
% number of coins lost.
model(Instance, Bags, [bags-Bags]) :-
    Total = Instance.total_coins_lost,
    Coins = Instance.coin_numbers,
    length(Coins, N),
    length(Bags, N),
    Bags ins 0..Total,
    scalar_product(Coins, Bags, #=, Total).
