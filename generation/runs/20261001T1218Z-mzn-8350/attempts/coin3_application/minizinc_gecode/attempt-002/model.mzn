% Coins: choose how many coins of each denomination to hold, as few as possible
% in total, so that every amount from 1 up to max_amount_to_pay - 1 can be paid
% exactly with a subset of the held coins.
include "globals.mzn";

array[int] of int: denominations;  % value of each kind of coin
int: max_amount_to_pay;            % every amount below this must be payable

set of int: Kinds = index_set(denominations);
int: n = card(Kinds);
set of int: Amounts = 1..max_amount_to_pay - 1;

% x[i] = number of coins of kind i that are held
array[Kinds] of var 0..max_amount_to_pay: x;

% the total number of coins held, to be minimised
var 0..max_amount_to_pay: num_coins;
constraint num_coins = sum(x);

% Which amounts can be paid is worked out kind by kind, instead of choosing
% for every amount how many coins of each kind pay it. Only x is part of the
% answer, and those per-amount choices would leave many equivalent ways of
% paying for the same x, which the enumeration of optimal answers would
% have to run through one by one.
%   can[j, v]    = the amount v can be paid with the held coins of kinds 1..j
%   needed[j, v] = the fewest coins of kind j that, together with coins of the
%                  kinds before it, pay v; `never` if no number does
int: never = max_amount_to_pay + 1;
array[0..n, 0..max_amount_to_pay - 1] of var bool: can;
array[1..n, 0..max_amount_to_pay - 1] of var 0..never: needed;

% with no kinds only the amount 0 can be paid
constraint forall(v in 0..max_amount_to_pay - 1) (can[0, v] <-> v = 0);

% v is paid without any coin of kind j if the earlier kinds pay it; otherwise
% one more coin of kind j than what is needed for v minus its value
constraint forall(j in 1..n, v in 0..max_amount_to_pay - 1)
    (needed[j, v] = if can[j - 1, v] then 0
                    elseif v >= denominations[j] then min(needed[j, v - denominations[j]] + 1, never)
                    else never endif);

% the held coins of kind j are enough to pay v
constraint forall(j in 1..n, v in 0..max_amount_to_pay - 1) (can[j, v] <-> needed[j, v] <= x[j]);

% every amount below the maximum is paid exactly, using only coins that are held
constraint forall(a in Amounts) (can[n, a]);

var int: objective = num_coins;
solve minimize objective;

output ["{\"x\": [", join(", ", [show(x[i]) | i in Kinds]), "]}"];
