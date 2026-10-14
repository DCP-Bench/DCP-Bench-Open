:- use_module(library(clpfd)).

% Chess set: a joinery makes small and large boxwood chess sets. Decide how
% many of each to make in a week so that the lathe hours and the boxwood are not
% exceeded and the profit is as large as possible.
%
% The problem statement fixes all the numbers; the instance carries no data.
model(_Instance, [Small, Large, Profit],
      [small_set-Small, large_set-Large, max_profit-Profit], max(Profit)) :-
    % number of small and large sets made per week (at most 100 of each is ever useful)
    [Small, Large] ins 0..100,
    Profit in 0..10000,

    % boxwood: a small set needs 1 kg, a large one 3 kg, and only 200 kg is available
    Small + 3 * Large #=< 200,
    % lathe hours: 3 hours per small set, 2 per large set, 4 lathes x 40 hours = 160 hours
    3 * Small + 2 * Large #=< 160,
    % profit: $5 per small set and $20 per large set
    Profit #= 5 * Small + 20 * Large.
