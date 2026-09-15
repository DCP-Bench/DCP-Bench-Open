include "globals.mzn";

int: n;
array[int, int] of int: adjacency_list;

set of int: Nodes = index_set_1of2(adjacency_list);
set of int: Slots = index_set_2of2(adjacency_list);
array[Nodes] of var bool: nodes;

% adjacency_list names neighbours 1-based.
constraint forall(i in Nodes, s in Slots where i < adjacency_list[i, s]) (
    bool2int(nodes[i]) + bool2int(nodes[adjacency_list[i, s]]) <= 1);
% Maximality: selected, or next to something selected.
constraint forall(i in Nodes) (
    nodes[i] \/ exists(s in Slots) (nodes[adjacency_list[i, s]]));

solve satisfy;

output ["{\"nodes\": [", join(", ", [show(nodes[i]) | i in Nodes]), "]}"];
