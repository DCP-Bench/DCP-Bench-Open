% Bus scheduling: the day is cut into equal time slots and a bus works two
% consecutive slots. Choose how many buses start in each slot so that every
% slot's demand is met with as few buses as possible.
include "globals.mzn";

array[int] of int: demands;  % buses needed in each slot
int: slots = card(index_set(demands));

% x[i] = number of buses that start working in slot i
array[1..slots] of var 0..sum(demands): x;

% a bus covers its starting slot and the next one (the day wraps around), so
% slot i+1 is served by the buses starting in slots i and i+1
constraint forall(i in 1..slots) (x[i] + x[i mod slots + 1] >= demands[i mod slots + 1]);

% use as few buses as possible
var int: objective = sum(x);
solve minimize objective;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 1..slots]), "]}"];
