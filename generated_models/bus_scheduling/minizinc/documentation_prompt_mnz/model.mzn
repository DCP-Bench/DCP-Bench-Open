include "globals.mzn";

% Input data
int: num_slots = 6;
array[1..num_slots] of int: demands = [4, 8, 10, 7, 12, 4];

% Each bus can operate 8 successive hours = 2 successive 4-hour slots
% Decision variables:
% x[i] = number of buses starting their 8-hour shift at time slot i
array[1..num_slots] of var 0..sum(demands): x;

% Constraints:
% For each time slot j, the number of buses available is the sum of buses
% that started at slot j and at slot j-1 (if j > 1)
% Because shifts last 2 slots, buses starting at slot i cover slots i and i+1
% For the last slot, only buses starting at that slot count (no next slot)
% We consider the schedule cyclic or not? Problem does not specify cyclic shifts,
% so no wrap-around.

constraint
  forall(j in 1..num_slots) (
    let {
      var int: buses_available = x[j] + if j > 1 then x[j-1] else 0 endif
    } in
    buses_available >= demands[j]
  );

% Objective: minimize total number of buses scheduled
solve minimize sum(x);

output [
  "{",
  join(",", [
    "\"" ++ "x" ++ "\": " ++ show(x)
  ]),
  "}"
];