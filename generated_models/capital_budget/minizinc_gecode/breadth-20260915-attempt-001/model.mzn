include "globals.mzn";

int: budget;
array[int] of int: npv;
array[int] of int: cash_flow;

set of int: Investments = index_set(npv);
array[Investments] of var bool: x;
var 0..sum(npv): z;

constraint sum(i in Investments) (cash_flow[i] * bool2int(x[i])) <= budget;
constraint z = sum(i in Investments) (npv[i] * bool2int(x[i]));

var int: objective = z;
solve maximize objective;

output ["{\"z\": ", show(z), ", \"x\": [", join(", ", [show(x[i]) | i in Investments]), "]}"];
