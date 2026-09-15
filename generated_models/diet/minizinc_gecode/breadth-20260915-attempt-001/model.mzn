include "globals.mzn";

int: n;
array[int] of int: price;
array[int] of int: limits;

% The reference's own constants: one row per nutrient, one column per food.
array[1..4] of array[1..4] of int: nutrients =
  [[400, 200, 150, 500], [3, 2, 0, 0], [2, 2, 4, 4], [2, 4, 1, 5]];

array[1..n] of var 0..10000: x;
var 0..1000: cost;

constraint forall(k in 1..4) (sum(i in 1..n) (nutrients[k][i] * x[i]) >= limits[k]);
constraint cost = sum(i in 1..n) (price[i] * x[i]);

var int: objective = cost;
solve minimize objective;

output ["{\"cost\": ", show(cost), "}"];
