% Problem: session1_money_change
% Alice has to give Bob change with coins of several types. Each type has a value
% and a number of coins available. Choose how many coins of each type to give so
% that the total equals the amount, and the number of coins used is minimal.
% Output coin_counts: the number of coins of each type given to Bob.

:- lib(ic).

model(Instance, Counts, [coin_counts-Counts], min(Coins)) :-
    memberchk(amount-Amount, Instance),
    memberchk(types_of_coins-Values, Instance),
    memberchk(available_coins-Available, Instance),
    length(Values, N),
    length(Counts, N),

    % She has a certain number of coins of each value available.
    ( foreach(C, Counts), foreach(A, Available) do
        C :: 0..A
    ),

    % The change must add up to the amount, using coins of the given values.
    ( foreach(C, Counts), foreach(V, Values), fromto(0, S0, S1, Total) do
        S1 #= S0 + V * C
    ),
    Total #= Amount,

    % Minimise the number of coins used.
    Coins #= sum(Counts).
