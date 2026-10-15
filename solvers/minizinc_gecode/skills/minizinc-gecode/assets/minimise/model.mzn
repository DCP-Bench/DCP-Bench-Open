% Minimum vertex cover: the fewest nodes such that every edge has at
% least one endpoint chosen. The graph is the 7 edges below on nodes 1..6.
int: n = 6;
array[1..7, 1..2] of 1..n: edges = [| 1, 2 | 1, 3 | 2, 3 | 2, 4 | 3, 5 | 4, 5 | 5, 6 |];

array[1..n] of var bool: in_cover;
var 0..n: size = sum(i in 1..n)(bool2int(in_cover[i]));

constraint forall(e in 1..7)(in_cover[edges[e, 1]] \/ in_cover[edges[e, 2]]);

solve minimize size;

output ["cover: ", show([i | i in 1..n where in_cover[i]]), "\n",
        "size = ", show(size), "\n"];
