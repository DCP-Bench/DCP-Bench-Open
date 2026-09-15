include "globals.mzn";

array[int] of int: available_seats;
array[int] of int: demand;
array[int] of int: revenue;
array[int, int] of int: delta;

set of int: Packages = index_set(demand);
set of int: Legs = index_set(available_seats);
array[Packages] of var 0..max(demand): packages_to_sell;

constraint forall(j in Legs) (
    sum(i in Packages) (delta[i, j] * packages_to_sell[i]) <= available_seats[j]);
constraint forall(i in Packages) (packages_to_sell[i] <= demand[i]);

var int: objective = sum(i in Packages) (revenue[i] * packages_to_sell[i]);
solve maximize objective;

output ["{\"packages_to_sell\": [", join(", ", [show(packages_to_sell[i]) | i in Packages]),
        "], \"max_revenue\": ", show(objective), "}"];
