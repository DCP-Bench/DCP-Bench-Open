include "globals.mzn";

% Coin denominations in cents
array[1..6] of int: coins = [1, 2, 5, 10, 20, 50];

% Decision variables: number of each coin used
array[1..6] of var 0..100: x;

% Maximum amount to pay (less than one Euro)
int: max_amount = 99;

% For each amount from 1 to 99, we must be able to pay exactly using the coins chosen
% We model this by checking that for each amount, there exists a combination of coins (y)
% with y[i] <= x[i] that sums to the amount.

% To model this, we introduce auxiliary variables y[a,i] for each amount a and coin i
array[1..max_amount, 1..6] of var 0..100: y;

% Constraints:
constraint
  forall(a in 1..max_amount) (
    % sum of y[a,i]*coins[i] = a
    sum(i in 1..6)(y[a,i] * coins[i]) = a /\
    % y[a,i] <= x[i]
    forall(i in 1..6)(y[a,i] <= x[i])
  );

% Objective: minimize total number of coins used
var int: total_coins = sum(i in 1..6)(x[i]);
solve minimize total_coins;

output [
  "{",
  "\"x\": ", show(x),
  "}"
];