include "globals.mzn";

int: total_price;
int: num_items;

array[1..num_items] of var 1..total_price: prices;

constraint sum(i in 1..num_items) (prices[i]) = total_price;
constraint product(i in 1..num_items) (prices[i]) = total_price * pow(100, num_items - 1);

solve satisfy;

output ["{\"prices\": [", join(", ", [show(prices[i]) | i in 1..num_items]), "]}"];
