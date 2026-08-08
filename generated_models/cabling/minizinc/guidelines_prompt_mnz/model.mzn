
include "globals.mzn";

% Decision variables: rack positions for each device (1..8 U units)
var 1..8: pos_A;
var 1..8: pos_B;
var 1..8: pos_C;
var 1..8: pos_D;
var 1..8: pos_E;
var 1..8: pos_F;
var 1..8: pos_G;
var 1..8: pos_H;

array[1..8] of var 1..8: pos = [
    pos_A, pos_B, pos_C, pos_D, pos_E, pos_F, pos_G, pos_H
];

% All devices must occupy distinct U positions
constraint all_different(pos);

% Calculate total cable length weighted by number of cables
var 0..100: final_sum;
constraint
    final_sum =
      1 * abs(pos_A - pos_H)  % A-H: 1 cable
    + 2 * abs(pos_A - pos_E)  % A-E: 2 cables
    + 4 * abs(pos_B - pos_F)  % B-F: 4 cables
    + 1 * abs(pos_C - pos_G)  % C-G: 1 cable
    + 1 * abs(pos_C - pos_D)  % C-D: 1 cable
    + 1 * abs(pos_C - pos_E)  % C-E: 1 cable
    + 3 * abs(pos_D - pos_H)  % D-H: 3 cables
    + 1 * abs(pos_G - pos_H); % G-H: 1 cable

% Optimize to minimize the total cable length
solve minimize final_sum;

% Output result in JSON format
output [
    "{",
    "\"final_sum\": " ++ show(final_sum),
    "}"
];
