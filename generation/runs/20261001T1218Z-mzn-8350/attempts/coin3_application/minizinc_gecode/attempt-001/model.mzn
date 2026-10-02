% Coins: choose how many coins of each denomination to hold, as few as possible
% in total, so that every amount from 1 up to max_amount_to_pay - 1 can be paid
% exactly with a subset of the held coins.
include "globals.mzn";

array[int] of int: denominations;  % value of each kind of coin
int: max_amount_to_pay;            % every amount below this must be payable

set of int: Kinds = index_set(denominations);
set of int: Amounts = 1..max_amount_to_pay - 1;

% x[i] = number of coins of kind i that are held
array[Kinds] of var 0..max_amount_to_pay: x;

% pay[a, i] = number of coins of kind i used to pay the amount a
array[Amounts, Kinds] of var 0..max_amount_to_pay: pay;

% the total number of coins held, to be minimised
var 0..max_amount_to_pay: num_coins;
constraint num_coins = sum(x);

% every amount below the maximum is paid exactly, using only coins that are held
constraint forall(a in Amounts) (sum(i in Kinds) (pay[a, i] * denominations[i]) = a);
constraint forall(a in Amounts, i in Kinds) (pay[a, i] <= x[i]);

% Implied: paying a with coins of value d takes at most a div d of them. It
% follows from the exact-sum constraint above, removes no solution, and gives
% Gecode a tighter bound on how many coins of each kind are needed.
constraint forall(a in Amounts, i in Kinds) (pay[a, i] <= a div denominations[i]);

var int: objective = num_coins;
solve minimize objective;

output ["{\"x\": [", join(", ", [show(x[i]) | i in Kinds]), "]}"];
