include "globals.mzn";

% Input data
int: m = 16; % Number of edges
int: n = 8;  % Number of nodes
array[1..m, 1..2] of int: graph = 
  [| 0, 1
   | 0, 2
   | 0, 3
   | 1, 2
   | 1, 3
   | 2, 3
   | 4, 5
   | 4, 6
   | 4, 7
   | 5, 6
   | 5, 7
   | 6, 7
   | 0, 4
   | 1, 5
   | 2, 6
   | 3, 7 |];

% Decision variables
% Node labels: unique labels from 0..m (since q = m edges)
array[0..n-1] of var 0..m: nodes;

% Edge labels: absolute difference of node labels for each edge
array[1..m] of var 1..m: edges;

% Constraints

% All node labels are distinct
constraint all_different(nodes);

% Edge labels are absolute differences of node labels
constraint forall(e in 1..m) (
  edges[e] = abs(nodes[graph[e,1]] - nodes[graph[e,2]])
);

% All edge labels are distinct
constraint all_different(edges);

solve satisfy;

output [
  "{",
  "\"nodes\": ", show(nodes), ",",
  "\"edges\": ", show(edges),
  "}"
];