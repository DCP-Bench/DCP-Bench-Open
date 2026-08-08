% Tommy's coins problem: half-crowns, shillings, and sixpence coins
% Given:
% - Total coins = 15
% - Total amount = £1 5s 6d = 1 pound + 5 shillings + 6 pence
%   1 pound = 20 shillings, 1 shilling = 12 pence
%   So total pence = (1 * 20 * 12) + (5 * 12) + 6 = 240 + 60 + 6 = 306 pence
% Coins:
% - half-crown = 2 shillings 6 pence = 30 pence
% - shilling = 12 pence
% - sixpence = 6 pence

include "globals.mzn";

% Decision variables: number of each coin
var 0..15: half_crowns;
var 0..15: shillings;
var 0..15: sixpence;

% Constraints
constraint half_crowns + shillings + sixpence == 15;
constraint half_crowns * 30 + shillings * 12 + sixpence * 6 == 306;

solve satisfy;

output [
    "{",
    "\"half_crowns\": ", show(half_crowns),
    "}"
];