include "globals.mzn";

% Number of countries
int: n = 6;

% Adjacency list given as pairs (i, j)
array[1..9, 1..2] of int: graph = [
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

% Decision variables: colors assigned to each country (1..n)
array[1..n] of var 1..n: colors;

% The maximum color used
var 1..n: max_color = max(colors);

% Constraints: adjacent countries must have different colors
constraint
    forall(e in 1..length(graph)) (
        colors[graph[e,1]] != colors[graph[e,2]]
    );

% Objective: minimize the number of colors used
solve minimize max_color;

output [
    "{",
    "\"colors\": ", show(colors),
    "}"
];