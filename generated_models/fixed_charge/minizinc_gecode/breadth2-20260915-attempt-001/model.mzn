include "globals.mzn";

int: num_machines;
int: num_products;
array[int] of int: machines;
array[int] of int: products;
array[int] of int: resources;
array[int] of int: renting_cost;
array[int] of int: capacity;
int: max_production;
array[int, int] of int: product;
array[int, int] of int: use;
int: shirtM; int: shortM; int: pantM;
int: shirt; int: shorts; int: pants;
int: labor; int: cloth;

set of int: Machines = 1..num_machines;
set of int: Products = 1..num_products;
set of int: Resources = index_set(resources);

array[Machines] of var bool: rent;
array[Products] of var 0..max_production: produce;
var 0..10000: z;

constraint z = sum(p in Products) (product[p, 1] * produce[p])
              - sum(m in Machines) (renting_cost[m] * bool2int(rent[m]));
constraint forall(r in Resources) (
    sum(p in Products) (use[p, r] * produce[p]) <= capacity[r]);
% The reference pairs product p with machine p.
constraint forall(p in Products) (produce[p] <= max_production * bool2int(rent[p]));

var int: objective = z;
solve maximize objective;

output ["{\"z\": ", show(z), "}"];
