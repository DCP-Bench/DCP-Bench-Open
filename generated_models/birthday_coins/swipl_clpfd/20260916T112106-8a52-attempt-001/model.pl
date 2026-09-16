:- use_module(library(clpfd)).

% Birthday coins: fifteen old British coins worth one pound five and six.
% Working in pence: a half-crown is 30, a shilling 12, a sixpence 6.
model(_Instance, Coins, [half_crowns-HalfCrowns]) :-
    length(Coins, 3),
    Coins ins 0..15,
    Coins = [HalfCrowns|_],
    scalar_product([30, 12, 6], Coins, #=, 306),
    sum(Coins, #=, 15).
