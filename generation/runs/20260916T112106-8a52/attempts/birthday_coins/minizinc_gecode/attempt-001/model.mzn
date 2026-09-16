% Birthday coins: fifteen old British coins worth one pound five and six.
% Working in pence: a half-crown is 30, a shilling 12, a sixpence 6.
array[1..3] of int: values = [30, 12, 6];
array[1..3] of var 0..15: coins;

constraint sum(i in 1..3) (values[i] * coins[i]) = 240 + 5 * 12 + 6;
constraint sum(coins) = 15;

solve satisfy;

output ["{\"half_crowns\": ", show(coins[1]), "}"];
