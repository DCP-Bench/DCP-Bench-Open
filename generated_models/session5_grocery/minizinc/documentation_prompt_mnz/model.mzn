include "globals.mzn";

% The total price in cents
int: total = 711;

% Decision variables: prices of the four items in cents
array[1..4] of var 1..total: prices;

% Constraint: sum of prices equals total
constraint sum(prices) == total;

% Constraint: product of prices equals total^4 (since prices are in cents, product should be total in cents)
% Actually, the product of the four prices in cents should be 711 cents, but product of four integers each <= 711 is huge.
% The problem states the product of the four prices equals 7.11 dollars, i.e., 711 cents.
% But product of four prices in cents equals 711 is unlikely.
% The original problem is known: the sum of the four prices is $7.11 and the product of the four prices is $7.11.
% So the product of the prices in dollars is 7.11, but prices are in cents.
% So product of prices in cents is 7.11 * 100^4 = 7.11 * 100000000 = 711000000
% So product of prices in cents = 711000000

constraint
  let {
    var int: prod = prices[1] * prices[2] * prices[3] * prices[4]
  } in
    prod == 711000000;

% Prices should be in ascending order to avoid symmetric solutions
constraint prices[1] <= prices[2] /\ prices[2] <= prices[3] /\ prices[3] <= prices[4];

solve satisfy;

output [
    "{",
    "\"prices\": ", show(prices),
    "}"
];