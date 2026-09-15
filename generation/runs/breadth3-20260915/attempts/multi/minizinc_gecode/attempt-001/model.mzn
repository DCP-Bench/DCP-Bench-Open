include "globals.mzn";

array[int, int] of int: supply;
array[int, int] of int: demand;
array[int, int] of int: limit;
array[int, int, int] of int: cost;

set of int: Origins = index_set_1of2(supply);
set of int: Destinations = index_set_1of2(demand);
set of int: Products = index_set_2of2(supply);
int: ceiling = max(i in Origins, p in Products) (supply[i, p]);
int: most = sum(i in Origins, p in Products) (supply[i, p])
          * max(i in Origins, j in Destinations, p in Products) (cost[i, j, p]);

array[Origins, Destinations, Products] of var 0..ceiling: x;
var 0..most: total_cost;

constraint forall(i in Origins, p in Products) (
    sum(j in Destinations) (x[i, j, p]) <= supply[i, p]);
constraint forall(j in Destinations, p in Products) (
    sum(i in Origins) (x[i, j, p]) >= demand[j, p]);
constraint forall(i in Origins, j in Destinations) (
    sum(p in Products) (x[i, j, p]) <= limit[i, j]);
constraint total_cost = sum(i in Origins, j in Destinations, p in Products) (
    cost[i, j, p] * x[i, j, p]);

var int: objective = total_cost;
solve minimize objective;

output ["{\"total_cost\": ", show(total_cost), "}"];
