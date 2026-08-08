
% Include necessary libraries
include "globals.mzn";

% Input data
int: target = 20;  % Target number of beers

% Compute upper bounds for decision variables to keep domains finite
int: max7 = (target + 7 - 1) div 7;    % Maximum number of 7-packs needed
int: max13 = (target + 13 - 1) div 13; % Maximum number of 13-packs needed

% Decision Variables
var 0..max7: x7;    % Number of 7-packs
var 0..max13: x13;  % Number of 13-packs

% Auxiliary variable for total beers
var int: total = 7 * x7 + 13 * x13;

% Constraint: meet or exceed the target
constraint total >= target;

% Objective: minimize the total number of beers (closest above target)
solve minimize total;

% Output in JSON format
output [
  "{",
    "\"counts\": [" ++ show(x7) ++ "," ++ show(x13) ++ "]",
  "}"
];
