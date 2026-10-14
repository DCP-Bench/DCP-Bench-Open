:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Coins: find the fewest coins, of the given denominations, that allow paying
% exactly any amount from 1 up to just below a given maximum.
model(Instance, Vars, [x-X], min(NumCoins)) :-
    Denominations = Instance.denominations,       % coin values
    MaxAmount = Instance.max_amount_to_pay,       % amounts 1..MaxAmount-1 must be payable

    % X[i] = number of coins of denomination i in the purse
    length(Denominations, N),
    length(X, N),
    X ins 0..MaxAmount,

    % the number of coins in the purse, which is minimised
    NumCoins in 0..MaxAmount,
    sum(X, #=, NumCoins),

    % every amount from 1 to MaxAmount-1 can be paid with coins of the purse:
    % Payments has, for each amount, how many coins of each denomination are used
    Last is MaxAmount - 1,
    numlist(1, Last, Amounts),
    maplist(payment(Denominations, X, MaxAmount), Amounts, Payments),
    append(Payments, PaymentVars),
    append(X, [NumCoins|PaymentVars], Vars).

% Pay Amount exactly: the coins used have the value Amount and no denomination
% is used more often than the purse holds it.
payment(Denominations, X, MaxAmount, Amount, Used) :-
    length(Denominations, N),
    length(Used, N),
    Used ins 0..MaxAmount,
    scalar_product(Denominations, Used, #=, Amount),
    maplist([U, Held]>>(U #=< Held), Used, X).

% Decide the purse first; the payments are found afterwards.
labeling_options([leftmost]).
