include "globals.mzn";

% Input data
int: nbHouses = 15;
int: MarioHouse = 1;
int: LuigiHouse = 2;
int: fuelMax = 2000;
int: goldTotalAmount = 1500;

array[1..nbHouses, 1..nbHouses] of int: conso = [
    | 0, 221, 274, 808, 13, 677, 670, 921, 943, 969, 13, 18, 217, 86, 322
    | 0, 0, 702, 83, 813, 679, 906, 246, 335, 529, 719, 528, 451, 242, 712
    | 274, 702, 0, 127, 110, 72, 835, 5, 161, 430, 686, 664, 799, 523, 73
    | 808, 83, 127, 0, 717, 80, 31, 71, 683, 668, 248, 826, 916, 467, 753
    | 13, 813, 110, 717, 0, 951, 593, 579, 706, 579, 101, 551, 280, 414, 294
    | 677, 679, 72, 80, 951, 0, 262, 12, 138, 222, 146, 571, 907, 225, 938
    | 670, 906, 835, 31, 593, 262, 0, 189, 558, 27, 287, 977, 226, 454, 501
    | 921, 246, 5, 71, 579, 12, 189, 0, 504, 221, 483, 226, 38, 314, 118
    | 943, 335, 161, 683, 706, 138, 558, 504, 0, 949, 393, 721, 267, 167, 420
    | 969, 529, 430, 668, 579, 222, 27, 221, 949, 0, 757, 747, 980, 589, 528
    | 13, 719, 686, 248, 101, 146, 287, 483, 393, 757, 0, 633, 334, 492, 859
    | 18, 528, 664, 826, 551, 571, 977, 226, 721, 747, 633, 0, 33, 981, 375
    | 217, 451, 799, 916, 280, 907, 226, 38, 267, 980, 334, 33, 0, 824, 491
    | 86, 242, 523, 467, 414, 225, 454, 314, 167, 589, 492, 981, 824, 0, 143
    | 322, 712, 73, 753, 294, 938, 501, 118, 420, 528, 859, 375, 491, 143, 0
];

array[1..nbHouses] of int: goldInHouse = [0, 0, 40, 67, 89, 50, 6, 19, 47, 68, 94, 86, 34, 14, 14];

% Decision variables
% We model the route as a successor array: for each house s, succ[s] is the next house visited after s.
array[1..nbHouses] of var 1..nbHouses: succ;

% We want a path starting at MarioHouse and ending at LuigiHouse.
% To model this, we will:
% - enforce that LuigiHouse has no successor (succ[LuigiHouse] = LuigiHouse)
% - enforce that MarioHouse is the start (no other house points to MarioHouse)
% - ensure the route is a path (no cycles except the LuigiHouse self-loop)

% Constraints

% LuigiHouse is the end: it points to itself (no successor)
constraint succ[LuigiHouse] = LuigiHouse;

% No house points to MarioHouse (except MarioHouse itself if needed)
% We want MarioHouse to be the start, so no other house can have succ = MarioHouse
constraint forall(h in 1..nbHouses where h != MarioHouse) (
    succ[h] != MarioHouse
);

% The route forms a path from MarioHouse to LuigiHouse:
% We use a subcircuit constraint to allow a subcircuit (a cycle or self-loop)
% We want exactly one cycle: the LuigiHouse self-loop
% So the subcircuit formed by succ should have exactly one cycle of length 1 at LuigiHouse,
% and the rest is a path from MarioHouse to LuigiHouse.

% To enforce this, we use subcircuit(succ) and ensure that the only cycle is LuigiHouse's self-loop.

% subcircuit(succ) means the graph formed by succ is a set of disjoint cycles covering all nodes.
% We want exactly one cycle of length 1 at LuigiHouse, and the rest is a path starting at MarioHouse.

% We enforce that the cycle count is 1 and that cycle is LuigiHouse's self-loop.

% We can enforce that for all houses except LuigiHouse, succ[s] != s (no self-loop except LuigiHouse)
constraint forall(s in 1..nbHouses where s != LuigiHouse) (
    succ[s] != s
);

% subcircuit constraint
constraint subcircuit(succ);

% To ensure the path starts at MarioHouse, we enforce that MarioHouse is not pointed to by any other house
% (already done above), and that from MarioHouse we can reach LuigiHouse by following succ.

% We define an array to represent the order of houses visited in the path
array[1..nbHouses] of var 0..nbHouses: position; % 0 means not visited

% MarioHouse is at position 1
constraint position[MarioHouse] = 1;

% LuigiHouse is visited and has position > 0
constraint position[LuigiHouse] > 0;

% For all houses except LuigiHouse, if position[s] > 0 then position[succ[s]] = position[s] + 1
constraint forall(s in 1..nbHouses where s != LuigiHouse) (
    (position[s] > 0) -> (position[succ[s]] = position[s] + 1)
);

% For houses not in the path, position = 0
% This is ensured by the above constraints and subcircuit.

% The path length is position[LuigiHouse]
var 1..nbHouses: pathLength = position[LuigiHouse];

% Fuel consumption along the path must not exceed fuelMax
var 0..fuelMax: totalFuel;

constraint totalFuel = sum(s in 1..nbHouses where position[s] > 0 /\ s != LuigiHouse) (
    conso[s, succ[s]]
);

constraint totalFuel <= fuelMax;

% Gold collected is sum of gold in visited houses (position > 0)
var 0..goldTotalAmount: goldCollected;

constraint goldCollected = sum(s in 1..nbHouses where position[s] > 0) (
    goldInHouse[s]
);

% Objective: maximize goldCollected
solve maximize goldCollected;

% Output the successor list as a list of 15 integers
output [
    "{",
    join(",", [
        "\"" ++ "s" ++ "\": [" ++ join(",", [show(succ[i]) | i in 1..nbHouses]) ++ "]"
    ]),
    "}"
];