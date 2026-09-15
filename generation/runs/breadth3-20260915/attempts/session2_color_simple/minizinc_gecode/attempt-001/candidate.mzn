include "globals.mzn";

array[int, int] of int: graph;

set of int: Edges = index_set_1of2(graph);
% The reference fixes the country count; it is the largest 1-based node id.
int: nodes = max(e in Edges, k in index_set_2of2(graph)) (graph[e, k]);
array[1..nodes] of var 1..nodes: colors;

constraint forall(e in Edges) (colors[graph[e, 1]] != colors[graph[e, 2]]);

var int: objective = max(k in 1..nodes) (colors[k]);
solve minimize objective;

output ["{\"colors\": [", join(", ", [show(colors[k]) | k in 1..nodes]), "]}"];
