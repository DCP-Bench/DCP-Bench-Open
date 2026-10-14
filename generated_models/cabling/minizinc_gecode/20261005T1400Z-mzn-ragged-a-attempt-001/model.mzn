% Cabling: place n one-unit devices in a rack, one per slot, so that the total
% length of the cables connecting them is as short as possible. A cable between
% slots p and q has length |p - q|, and a pair of devices may need several cables.
include "globals.mzn";

int: n;                                   % number of devices (and rack slots)
array[int] of string: devices;            % device names
% cable_struct rows are [device, device, number of cables]; the runner binds the
% string and integer columns as separate arrays.
array[int] of string: cable_struct_1;
array[int] of string: cable_struct_2;
array[int] of int: cable_struct_3;

set of int: Devices = index_set(devices);
set of int: Cables = index_set(cable_struct_3);

% the device index of a name, as the reference's device_map
function int: device(string: name) =
    let { array[int] of int: found = [d | d in Devices where devices[d] = name] }
    in assert(length(found) = 1, "unknown or duplicate device " ++ name, found[1]);

array[Cables] of int: end_a = [device(cable_struct_1[c]) | c in Cables];
array[Cables] of int: end_b = [device(cable_struct_2[c]) | c in Cables];

% x[d] = position of device d in the rack
array[Devices] of var 0..n-1: x;

% every device has its own position in the rack
constraint all_different(x);

% t[c] = length of cable row c: the distance between its two devices times the
% number of cables (domain 1..n*n as in the reference)
array[Cables] of var 1..n*n: t;
constraint forall(c in Cables) (t[c] = abs(x[end_a[c]] - x[end_b[c]]) * cable_struct_3[c]);

% minimise the sum of all cable lengths
var 0..n*n*sum(cable_struct_3): final_sum = sum(t);
var int: objective = final_sum;
solve minimize objective;

output ["{\"final_sum\": ", show(final_sum), "}"];
