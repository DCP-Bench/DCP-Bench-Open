# Graph colouring

Colour the nodes of an undirected graph so that the two endpoints of every edge
get different colours, using as **few** distinct colours as possible.

Instance: `{"n_nodes": 10, "edges": [[0, 1], ...]}`; nodes are numbered
`0 .. n_nodes-1`.

Print one optimal solution as `{"colour": [c_0, ..., c_{n_nodes-1}]}`, where
each `c_i` is a non-negative integer. The number of distinct values used is the
objective.
