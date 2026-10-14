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

    % Every amount from 1 to MaxAmount-1 can be paid with the purse. Instead of
    % choosing the coins that pay each amount (which makes the same purse appear
    % once per way of paying, and the search backtrack over those ways), the
    % payable amounts are computed from the purse one denomination at a time:
    % Reachable[s] is 1 when amount s can be paid with the denominations seen so
    % far. Nothing in it is a free choice, so each purse is found only once.
    Last is MaxAmount - 1,
    numlist(0, Last, Amounts),
    maplist([S, Flag]>>(S =:= 0 -> Flag = 1 ; Flag = 0), Amounts, Reachable0),
    foldl(add_denomination(MaxAmount), Denominations, X, Reachable0-[], Reachable-Used),
    Reachable = [_|MustPay],
    maplist(=(1), MustPay),
    append(Used, UsedVars),
    append(X, [NumCoins|UsedVars], Vars).

% Pay with one more denomination. Reachable0[s] says whether s is payable
% without it, Count is the number of coins of this denomination in the purse.
% Used[s] is the fewest coins of this denomination needed to pay s, or -1 when
% s cannot be paid with them: 0 if s was payable already, otherwise one more
% than for s - Denomination, as long as that stays within Count.
add_denomination(MaxAmount, Denomination, Count, Reachable0-Used0, Reachable-[Used|Used0]) :-
    length(Reachable0, Length),
    length(Used, Length),
    MinusOne is -1,
    Used ins MinusOne..MaxAmount,
    Last is Length - 1,
    numlist(0, Last, Amounts),
    maplist(used_coins(Reachable0, Used, Denomination, Count), Amounts),
    maplist([U, Flag]>>(Flag #<==> (U #>= 0)), Used, Reachable).

used_coins(Reachable0, Used, Denomination, Count, Amount) :-
    nth0(Amount, Reachable0, Before),
    nth0(Amount, Used, U),
    (   Amount >= Denomination
    ->  Back is Amount - Denomination,
        nth0(Back, Used, UBack),
        Before #= 1 #==> U #= 0,
        (Before #= 0 #/\ UBack #>= 0 #/\ UBack #< Count) #==> U #= UBack + 1,
        (Before #= 0 #/\ #\ (UBack #>= 0 #/\ UBack #< Count)) #==> U #= -1
    ;   U #= Before - 1
    ).

% Decide the purse first, in order of denomination; the payable amounts follow.
labeling_options([leftmost]).
