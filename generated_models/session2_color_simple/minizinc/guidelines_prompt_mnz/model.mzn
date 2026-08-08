
% Include necessary global constraints
include "globals.mzn";

% Number of countries
int: n = 6;

% Adjacency list: each pair indicates two neighbouring countries
array[1..9, 1..2] of int: graph = 
[
    | 3, 1
    | 3, 6
    | 3, 4
    | 6, 4
    | 6, 1
    | 1, 5
    | 1, 4
    | 4, 5
    | 4, 2
];

% Decision variables: color assigned to each country (1..n)
array[1..n] of var 1..n: colors;

% Constraint: neighbouring countries must have different colours
constraint
    forall(e in 1..9) (
        colors[ graph[e,1] ] != colors[ graph[e,2] ]
    );

% Auxiliary variable: the maximum colour used
var 1..n: max_color = max(colors);

% Objective: minimize the number of colours used
solve minimize max_color;

% Output the colouring as a JSON list under the key "colors"
output [
    "{",
    "\"colors\": [" ++ join(",", [ show(colors[i]) | i in 1..n ]) ++ "]",
    "}"
];
