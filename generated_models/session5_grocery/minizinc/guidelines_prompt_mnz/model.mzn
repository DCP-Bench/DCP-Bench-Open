
include "globals.mzn";

% We have four item prices in cents
array[1..4] of var 1..711: prices;

% The sum of the four prices must be 711 cents (i.e., $7.11)
constraint sum(i in 1..4)(prices[i]) = 711;

% The product of the four prices (in cents) must equal 711000000
% (since (p1/100)*(p2/100)*(p3/100)*(p4/100) = 7.11 
%  => p1*p2*p3*p4 = 7.11 * 100^4 = 711000000)
constraint prices[1] * prices[2] * prices[3] * prices[4] = 711000000;

% Symmetry‐breaking: enforce non‐decreasing order
constraint forall(i in 1..3)(prices[i] <= prices[i+1]);

solve satisfy;

output [
    "{",
    "\"prices\": [" ++ join(",", [show(prices[i]) | i in 1..4]) ++ "]",
    "}"
];
