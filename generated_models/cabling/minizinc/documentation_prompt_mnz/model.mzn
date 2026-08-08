include "globals.mzn";

% Devices and their indices
set of int: DEVICES = 1..8;
array[DEVICES] of string: device_names = ["A","B","C","D","E","F","G","H"];

% Number of units in the rack (1U per device)
int: num_units = 8;

% Connections between devices with number of cables
% Each tuple: (device1, device2, number_of_cables)
array[1..8] of tuple(device1: int, device2: int, cables: int) : connections = [
    (1, 8, 1), % A-H
    (1, 5, 2), % A-E
    (2, 6, 4), % B-F
    (3, 7, 1), % C-G
    (3, 4, 1), % C-D
    (3, 5, 1), % C-E
    (4, 8, 3), % D-H
    (7, 8, 1)  % G-H
];

int: num_connections = length(connections);

% Decision variables:
% pos[d] = position of device d in the rack (1..8)
array[DEVICES] of var 1..num_units: pos;

% All devices must be placed in different positions
constraint alldifferent(pos);

% Calculate cable lengths for each connection
array[1..num_connections] of var int: cable_lengths;

constraint
  forall(i in 1..num_connections) (
    let {
      int: d1 = connections[i].device1,
      int: d2 = connections[i].device2,
      int: cables = connections[i].cables
    } in
      cable_lengths[i] = cables * abs(pos[d1] - pos[d2])
  );

% Objective: minimize sum of all cable lengths
var int: final_sum = sum(cable_lengths);

solve minimize final_sum;

output [
  "{",
  "\"final_sum\": ", show(final_sum),
  "}"
];