
% Include global constraints library
include "globals.mzn";

% Decision Variables
var 0..100: men;
var 0..100: women;
var 0..100: children;

% Constraints
constraint
    % Total people
    men + women + children = 100 /\
    % Total bushels (3*men + 2*women + 0.5*children = 100) multiplied by 2 to keep integers:
    6 * men + 4 * women + children = 200 /\
    % There are five times as many women as men
    women = 5 * men;

solve satisfy;

% Output in JSON format
output [
    "{",
    join(",", [
        "\"" ++ "men" ++ "\": " ++ show(men),
        "\"" ++ "women" ++ "\": " ++ show(women),
        "\"" ++ "children" ++ "\": " ++ show(children)
    ]),
    "}"
];
