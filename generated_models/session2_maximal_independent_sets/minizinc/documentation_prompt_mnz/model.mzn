include "globals.mzn";

int: n = 8;
array[1..n] of array[int] of int: adjacency_list = [
    [2, 3, 7],
    [1, 4, 8],
    [1, 4, 5],
    [2, 3, 6],
    [3, 6, 7],
    [4, 5, 8],
    [1, 5, 8],
    [2, 6, 7]
];

% Decision variable: whether each node is included in the maximal independent set
array[1..n] of var bool: nodes;

% Constraint 1: Independent set - no two adjacent nodes can both be in the set
constraint
    forall(i in 1..n, j in adjacency_list[i]) (
        nodes[i] + nodes[j] <= 1
    );

% Constraint 2: Maximality - for each node not in the set, at least one neighbor must be in the set
constraint
    forall(i in 1..n) (
        (not nodes[i]) -> (exists(j in adjacency_list[i]) (nodes[j]))
    );

solve satisfy;

output [
    "{",
    join(",", [ "\"" ++ "nodes" ++ "\": " ++ show(nodes) ]),
    "}"
];